from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class StorySection(BaseModel):
    __tablename__ = "story_sections"

    story_id: Mapped[int] = mapped_column(Integer, ForeignKey("stories.id"), nullable=False)
    section_index: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    image_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    @property
    def has_image(self) -> bool:
        return bool(self.image_url)

    @property
    def has_audio(self) -> bool:
        return bool(self.audio_url)

    # Relationships
    story: Mapped["Story"] = relationship(back_populates="sections")


from app.models.story import Story  # noqa: E402
