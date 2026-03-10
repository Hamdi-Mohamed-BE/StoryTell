from loguru import logger
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from app.ai.chains.schemas import EnhancedImagePrompt

ENHANCE_PROMPT = """You are an expert AI image prompt engineer.

Transform this raw scene description into a high-quality prompt for AI image generation (Stable Diffusion / FLUX).

Raw description: "{raw_prompt}"

Story context: "{story_title}" ({story_type})

Rules:
- Add art style (cinematic illustration, anime style, digital painting, etc.)
- Add lighting and mood details
- Add composition and camera angle
- Add color palette hints
- NEVER include text, words, letters, or watermarks in the prompt
- Keep it under 150 words
- Make it vivid and specific"""


class PromptEnhancerChain:
    """Enhances raw image prompts using Gemini for better image generation results."""

    def __init__(self, api_key: str, gemeni_model: str = "gemini-3-flash-preview"):
        self.llm = ChatGoogleGenerativeAI(
            model=gemeni_model,
            google_api_key=api_key,
            temperature=0.8,
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("human", ENHANCE_PROMPT),
        ])
        self.chain = self.prompt | self.llm.with_structured_output(EnhancedImagePrompt)

    def enhance(self, raw_prompt: str, story_title: str = "", story_type: str = "") -> str:
        """Enhance a raw image prompt. Returns the refined prompt string."""
        result: EnhancedImagePrompt = self.chain.invoke({
            "raw_prompt": raw_prompt,
            "story_title": story_title,
            "story_type": story_type,
        })
        logger.debug(f"Enhanced prompt: {result.enhanced_prompt[:80]}...")
        return result.enhanced_prompt
