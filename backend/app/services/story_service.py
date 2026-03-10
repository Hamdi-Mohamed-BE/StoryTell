from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Story, StorySection, StoryGenerationJob
from app.services.cover_service import fetch_cover_url


class StoryService:
    """Handles story CRUD operations. All public lookups use uid."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_stories(self) -> list[Story]:
        result = await self.db.execute(
            select(Story).order_by(Story.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_uid(self, uid: str) -> Story | None:
        result = await self.db.execute(
            select(Story)
            .where(Story.uid == uid)
            .options(selectinload(Story.sections))
        )
        return result.scalar_one_or_none()

    async def create(self, title: str, story_type: str, description: str | None = None, author: str | None = None) -> Story:
        # Try to fetch a cover image from Open Library
        cover_image = await fetch_cover_url(title, author)

        story = Story(
            title=title,
            story_type=story_type,
            description=description,
            author=author,
            cover_image=cover_image,
        )
        self.db.add(story)
        await self.db.commit()
        await self.db.refresh(story)
        return story

    async def delete_by_uid(self, uid: str) -> bool:
        story = await self.get_by_uid(uid)
        if not story:
            return False
        await self.db.delete(story)
        await self.db.commit()
        return True

    async def get_sections(self, story_uid: str) -> list[StorySection]:
        story = await self.get_by_uid(story_uid)
        if not story:
            return []
        result = await self.db.execute(
            select(StorySection)
            .where(StorySection.story_id == story.id)
            .order_by(StorySection.section_index)
        )
        return list(result.scalars().all())

    async def get_section_by_uid(self, section_uid: str) -> StorySection | None:
        result = await self.db.execute(
            select(StorySection).where(StorySection.uid == section_uid)
        )
        return result.scalar_one_or_none()

    async def reset_story(self, uid: str) -> bool:
        """Delete all sections and generation jobs for a story (start fresh)."""
        story = await self.get_by_uid(uid)
        if not story:
            return False
        await self.db.execute(
            delete(StorySection).where(StorySection.story_id == story.id)
        )
        await self.db.execute(
            delete(StoryGenerationJob).where(StoryGenerationJob.story_id == story.id)
        )
        await self.db.commit()
        return True
