from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from loguru import logger

from app.workers.celery_app import celery_app
from app.config import get_settings
from app.models import Story, StorySection, StoryGenerationJob
from app.ai.chains.story_breakdown import StoryBreakdownChain
from app.ai.chains.prompt_enhancer import PromptEnhancerChain
from app.ai.chains.image_generator import ImageGenerator
from app.ai.chains.voice_generator import VoiceGenerator
from app.services import media_service


def _get_sync_session() -> Session:
    """Create a sync DB session for Celery tasks (Celery doesn't support async)."""
    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    return Session(engine)


@celery_app.task(bind=True, name="generate_story_sections")
def generate_story_sections(self, story_id: int, job_id: int):
    """
    Celery task: Generate story sections using Gemini AI.
    Pipeline: Story Breakdown → Prompt Enhancement → Image Generation (HuggingFace)
    AI decides how many sections are needed to cover the full story.
    """
    session = _get_sync_session()
    try:
        story = session.get(Story, story_id)
        job = session.get(StoryGenerationJob, job_id)

        if not story or not job:
            logger.error(f"Story {story_id} or Job {job_id} not found")
            return

        job.status = "processing"
        session.commit()

        settings = get_settings()

        # Fetch existing sections to continue from where we left off
        from sqlalchemy import select as sa_select
        existing_rows = session.execute(
            sa_select(StorySection.section_index, StorySection.title)
            .where(StorySection.story_id == story.id)
            .order_by(StorySection.section_index)
        ).all()
        existing_sections = [
            {"section_index": row.section_index, "title": row.title}
            for row in existing_rows
        ]

        # Step 1: Break story into sections via Gemini (AI decides section count)
        chain = StoryBreakdownChain(api_key=settings.google_api_key, gemeni_model=settings.gemeni_model)
        sections_data = chain.generate(
            story_title=story.title,
            story_type=story.story_type,
            description=story.description or "",
            existing_sections=existing_sections if existing_sections else None,
        )
        job.total_sections = len(sections_data)
        session.commit()

        # Step 2 & 3: Enhance prompts + generate images + generate voice
        enhancer = PromptEnhancerChain(api_key=settings.google_api_key, gemeni_model=settings.gemeni_model)
        image_gen = ImageGenerator(hf_token=settings.hf_token) if settings.hf_token else None
        voice_gen = None
        if settings.enable_audio_gen and settings.hf_token:
            voice_gen = VoiceGenerator(hf_token=settings.hf_token)
            logger.info("Audio generation ENABLED (HuggingFace TTS)")
        else:
            logger.info(f"Audio generation DISABLED — using sample URL")

        for section_data in sections_data:
            image_url = None
            audio_url = None
            raw_prompt = section_data.get("image_prompt")
            section_index = section_data["section_index"]

            if raw_prompt and image_gen:
                # Refine the raw prompt for better image generation
                enhanced_prompt = enhancer.enhance(
                    raw_prompt=raw_prompt,
                    story_title=story.title,
                    story_type=story.story_type,
                )
                logger.debug(f"Enhanced prompt: {enhanced_prompt[:80]}...")
                image_bytes = image_gen.generate(enhanced_prompt)
                if image_bytes:
                    image_url = media_service.save_image(story.id, section_index, image_bytes)

            # Generate voice narration for the section text
            if voice_gen:
                narration = f"{section_data['title']}. {section_data['text']}"
                audio_bytes = voice_gen.generate(narration)
                if audio_bytes:
                    audio_url = media_service.save_audio(story.id, section_index, audio_bytes)
            else:
                audio_url = settings.sample_audio_url

            section = StorySection(
                story_id=story.id,
                section_index=section_data["section_index"],
                title=section_data["title"],
                text=section_data["text"],
                image_prompt=raw_prompt,
                image_url=image_url,
                audio_url=audio_url,
            )
            session.add(section)
            job.generated_sections += 1

        job.status = "completed"
        session.commit()
        logger.info(f"Generated {len(sections_data)} sections for story '{story.title}'")

    except Exception as e:
        logger.exception(f"Failed to generate sections for story {story_id}")
        session.rollback()
        try:
            job = session.get(StoryGenerationJob, job_id)
            if job:
                job.status = "failed"
                job.error_message = str(e)[:500]
                session.commit()
        except Exception:
            pass
        raise
    finally:
        session.close()
