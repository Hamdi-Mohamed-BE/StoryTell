from sqlalchemy import String, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Story(BaseModel):
    __tablename__ = "stories"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    story_type: Mapped[str] = mapped_column(String(50), nullable=False)  # book, movie, anime, show
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cover_image: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    sections: Mapped[list["StorySection"]] = relationship(back_populates="story", cascade="all, delete-orphan")
    generation_jobs: Mapped[list["StoryGenerationJob"]] = relationship(back_populates="story", cascade="all, delete-orphan")


# Avoid circular import issues
from app.models.story_section import StorySection  # noqa: E402
from app.models.generation_job import StoryGenerationJob  # noqa: E402
