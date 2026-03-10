from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import StoryCreate, StoryOut, StoryDetailOut, StorySectionOut, StorySectionLight, GenerationJobOut
from app.services.story_service import StoryService
from app.services.generation_service import GenerationService

router = APIRouter(prefix="/api/stories", tags=["stories"])


# Static routes first (before /{story_uid} wildcard)
@router.get("/sections/{section_uid}/media", response_model=StorySectionOut)
async def get_section_media(section_uid: str, db: AsyncSession = Depends(get_db)):
    """Get a single section with full media (image_url, audio_url). Use for lazy loading."""
    service = StoryService(db)
    section = await service.get_section_by_uid(section_uid)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section


@router.get("", response_model=list[StoryOut])
async def list_stories(db: AsyncSession = Depends(get_db)):
    service = StoryService(db)
    stories = await service.list_stories()
    return stories


@router.post("", response_model=StoryOut, status_code=201)
async def create_story(data: StoryCreate, db: AsyncSession = Depends(get_db)):
    service = StoryService(db)
    story = await service.create(
        title=data.title,
        story_type=data.story_type,
        description=data.description,
        author=data.author,
    )
    return story


@router.get("/{story_uid}", response_model=StoryDetailOut)
async def get_story(story_uid: str, db: AsyncSession = Depends(get_db)):
    """Get story with lightweight sections (no base64 media data)."""
    service = StoryService(db)
    story = await service.get_by_uid(story_uid)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Convert sections to lightweight format with has_image/has_audio flags
    light_sections = []
    for s in story.sections:
        light_sections.append(StorySectionLight(
            uid=s.uid,
            section_index=s.section_index,
            title=s.title,
            text=s.text,
            image_prompt=s.image_prompt,
            has_image=bool(s.image_url),
            has_audio=bool(s.audio_url),
        ))

    return StoryDetailOut(
        uid=story.uid,
        title=story.title,
        description=story.description,
        story_type=story.story_type,
        author=story.author,
        cover_image=story.cover_image,
        created_at=story.created_at,
        sections=light_sections,
    )


@router.get("/{story_uid}/sections", response_model=list[StorySectionOut])
async def get_story_sections(story_uid: str, db: AsyncSession = Depends(get_db)):
    service = StoryService(db)
    sections = await service.get_sections(story_uid)
    return sections


@router.delete("/{story_uid}", status_code=204)
async def delete_story(story_uid: str, db: AsyncSession = Depends(get_db)):
    service = StoryService(db)
    deleted = await service.delete_by_uid(story_uid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Story not found")


@router.get("/{story_uid}/jobs", response_model=list[GenerationJobOut])
async def get_generation_jobs(story_uid: str, db: AsyncSession = Depends(get_db)):
    """List generation jobs for a story."""
    story_service = StoryService(db)
    story = await story_service.get_by_uid(story_uid)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    gen_service = GenerationService(db)
    jobs = await gen_service.get_jobs_for_story(story.id)
    return jobs


@router.delete("/{story_uid}/reset", status_code=204)
async def reset_story(story_uid: str, db: AsyncSession = Depends(get_db)):
    """Delete all sections and jobs for a story to start fresh."""
    service = StoryService(db)
    reset = await service.reset_story(story_uid)
    if not reset:
        raise HTTPException(status_code=404, detail="Story not found")
