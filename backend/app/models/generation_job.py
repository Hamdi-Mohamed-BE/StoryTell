from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class StoryGenerationJob(BaseModel):
    __tablename__ = "story_generation_jobs"

    story_id: Mapped[int] = mapped_column(Integer, ForeignKey("stories.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    total_sections: Mapped[int] = mapped_column(Integer, default=0)
    generated_sections: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    story: Mapped["Story"] = relationship(back_populates="generation_jobs")


from app.models.story import Story  # noqa: E402
