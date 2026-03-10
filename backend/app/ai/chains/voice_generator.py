from loguru import logger
from huggingface_hub import InferenceClient

DEFAULT_MODEL = "hexgrad/Kokoro-82M"


class VoiceGenerator:
    """Generates speech audio using HuggingFace InferenceClient (fal-ai provider)."""

    def __init__(self, hf_token: str, model: str = DEFAULT_MODEL):
        self.client = InferenceClient(provider="fal-ai", api_key=hf_token)
        self.model = model

    def generate(self, text: str) -> bytes | None:
        """Generate speech audio from text. Returns raw audio bytes or None on failure."""
        try:
            audio = self.client.text_to_speech(text, model=self.model)
            logger.debug(f"Audio generated ({len(audio)} bytes) for: {text[:50]}...")
            return audio
        except Exception as e:
            logger.warning(f"TTS failed: {e}")
            return None

