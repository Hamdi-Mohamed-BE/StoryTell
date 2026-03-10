from datetime import datetime
from pydantic import BaseModel, Field


# --- Story Schemas ---

class StoryCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    story_type: str = Field(..., max_length=50)  # book, movie, anime, show
    author: str | None = None


class StorySectionLight(BaseModel):
    """Lightweight section — no heavy base64 image/audio data."""
    uid: str
    section_index: int
    title: str
    text: str
    image_prompt: str | None = None
    has_image: bool = False
    has_audio: bool = False

    model_config = {"from_attributes": True}


class StorySectionOut(BaseModel):
    uid: str
    section_index: int
    title: str
    text: str
    image_prompt: str | None = None
    image_url: str | None = None
    audio_url: str | None = None

    model_config = {"from_attributes": True}


class StoryOut(BaseModel):
    uid: str
    title: str
    description: str | None = None
    story_type: str
    author: str | None = None
    cover_image: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class StoryDetailOut(StoryOut):
    sections: list[StorySectionLight] = []


# --- Generation Job Schemas ---

class GenerationJobOut(BaseModel):
    uid: str
    status: str
    total_sections: int
    generated_sections: int
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}



