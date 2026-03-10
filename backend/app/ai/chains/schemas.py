from pydantic import BaseModel, Field


class StoryCardSection(BaseModel):
    """A single story card representing one key moment in the narrative."""

    section_index: int = Field(description="Sequential index starting from 1")
    title: str = Field(description="Short scene title, 3-6 words")
    text: str = Field(
        description="Engaging narration text for this scene, 4-8 sentences long. "
        "Must be vivid and dramatic enough to fill 30 seconds to 1 minute of spoken audio."
    )
    image_prompt: str = Field(
        description="Detailed visual description for AI image generation. "
        "Include art style, lighting, mood, and composition details."
    )


class StoryBreakdownOutput(BaseModel):
    """Structured output containing all story card sections."""

    sections: list[StoryCardSection] = Field(
        description="Chronological list of story card sections"
    )


class EnhancedImagePrompt(BaseModel):
    """An enhanced, production-ready prompt optimized for AI image generation."""

    enhanced_prompt: str = Field(
        description="The refined image generation prompt. Should include: "
        "art style, composition, lighting, mood, color palette, and camera angle. "
        "Keep under 200 words. No text or words in the image."
    )
