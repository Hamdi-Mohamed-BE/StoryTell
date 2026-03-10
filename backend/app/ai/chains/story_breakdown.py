import json
from loguru import logger
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from app.ai.chains.schemas import StoryBreakdownOutput

STORY_BREAKDOWN_PROMPT = """You are a narrative summarization system for a visual story card app.

Break the ENTIRE story of "{story_title}" ({story_type}) into chronological moments — from the very beginning to the final ending.

{description_context}

{continuation_context}

IMPORTANT RULES:
- You decide how many sections are needed to cover the COMPLETE story from start to finish. Do NOT skip any major plot points.
- Each section's narration text MUST be long enough to fill 30 seconds to 1 minute of spoken audio. Write 4-8 sentences per section — vivid, engaging, and dramatic.
- Sections MUST follow the story's chronological order as it appears in the original work.
- Section indices must start at {start_index} and increment by 1.
- Each moment should capture a key scene that would make a compelling visual card.
- Include a detailed visual description for each scene suitable for AI image generation.
- Make the narration text engaging and immersive — write as if narrating to an audience, keeping them hooked."""


class StoryBreakdownChain:
    """Generates structured story sections using Google Gemini with Pydantic output."""

    def __init__(self, api_key: str, gemeni_model: str = "gemini-3-flash-preview"):
        self.llm = ChatGoogleGenerativeAI(
            model=gemeni_model,
            google_api_key=api_key,
            temperature=0.7,
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("human", STORY_BREAKDOWN_PROMPT),
        ])
        # Use with_structured_output for validated Pydantic responses
        self.chain = self.prompt | self.llm.with_structured_output(StoryBreakdownOutput)

    def generate(
        self,
        story_title: str,
        story_type: str,
        description: str = "",
        existing_sections: list[dict] | None = None,
    ) -> list[dict]:
        """Generate story breakdown sections. AI decides how many sections are needed to cover the full story."""

        description_context = f"Additional context: {description}" if description else ""

        # Build continuation context from previously generated sections
        start_index = 1
        continuation_context = ""
        if existing_sections:
            start_index = max(s["section_index"] for s in existing_sections) + 1
            section_summary = "\n".join(
                f"  {s['section_index']}. {s['title']}" for s in existing_sections
            )
            continuation_context = (
                f"The following sections have ALREADY been generated. "
                f"You MUST continue the story AFTER these events — do NOT repeat them:\n{section_summary}\n\n"
                f"Pick up the narrative right where section {start_index - 1} left off."
            )

        result: StoryBreakdownOutput = self.chain.invoke({
            "story_title": story_title,
            "story_type": story_type,
            "description_context": description_context,
            "continuation_context": continuation_context,
            "start_index": start_index,
        })

        # Force correct indices starting from start_index
        sections = []
        for i, section in enumerate(result.sections):
            data = section.model_dump()
            data["section_index"] = start_index + i
            sections.append(data)

        logger.info(f"Generated {len(sections)} sections for '{story_title}' (starting at index {start_index})")
        return sections
