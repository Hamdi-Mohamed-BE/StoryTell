from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Story, StoryGenerationJob
from app.workers.tasks import generate_story_sections


class GenerationService:
    """Handles story generation job management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_generation(self, story: Story) -> StoryGenerationJob:
        """Create a generation job and enqueue the Celery task."""
        job = StoryGenerationJob(
            story_id=story.id,
            status="pending",
            total_sections=0,  # AI decides how many sections
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        # Dispatch to Celery worker
        generate_story_sections.delay(story.id, job.id)

        return job

    async def get_job_by_uid(self, job_uid: str) -> StoryGenerationJob | None:
        result = await self.db.execute(
            select(StoryGenerationJob).where(StoryGenerationJob.uid == job_uid)
        )
        return result.scalar_one_or_none()

    async def get_jobs_for_story(self, story_id: int) -> list[StoryGenerationJob]:
        result = await self.db.execute(
            select(StoryGenerationJob)
            .where(StoryGenerationJob.story_id == story_id)
            .order_by(StoryGenerationJob.created_at.desc())
        )
        return list(result.scalars().all())
