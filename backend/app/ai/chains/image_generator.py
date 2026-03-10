from loguru import logger
import httpx

# Hugging Face Inference API (router.huggingface.co replaced api-inference.huggingface.co)
HF_API_URL = "https://router.huggingface.co/hf-inference/models"
# FLUX.1-schnell — fast, free-tier compatible
DEFAULT_MODEL = "black-forest-labs/FLUX.1-schnell"


class ImageGenerator:
    """Generates images using Hugging Face Inference API."""

    def __init__(self, hf_token: str, model: str = DEFAULT_MODEL):
        self.hf_token = hf_token
        self.model = model
        self.api_url = f"{HF_API_URL}/{self.model}"

    def generate(self, prompt: str, timeout: float = 120.0) -> bytes | None:
        """Send prompt to HF Inference API. Returns raw image bytes or None on failure."""
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        payload = {"inputs": prompt}

        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                resp = client.post(self.api_url, headers=headers, json=payload)

                if resp.status_code == 200:
                    content_type = resp.headers.get("content-type", "")
                    if "image" in content_type:
                        logger.debug(f"Image generated ({len(resp.content)} bytes) for: {prompt[:60]}...")
                        return resp.content

                # Model loading — HF returns 503 while model warms up
                if resp.status_code == 503:
                    logger.info("Model is loading on HF, retrying...")
                    import time
                    time.sleep(10)
                    resp = client.post(self.api_url, headers=headers, json=payload)
                    if resp.status_code == 200 and "image" in resp.headers.get("content-type", ""):
                        return resp.content

                logger.warning(f"HF returned {resp.status_code}: {resp.text[:200]}")

        except httpx.TimeoutException:
            logger.warning(f"Image generation timed out for: {prompt[:60]}...")
        except Exception as e:
            logger.warning(f"Image generation failed: {e}")
        return None

