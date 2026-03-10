from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "StoryCards"
    debug: bool = False

    # Logging
    app_logs_dir: str = "logs"

    # Media storage (local filesystem — swap for S3/GCS later)
    media_dir: str = "media"

    # Database
    database_url: str = "postgresql+asyncpg://storycards:storycards@db:5432/storycards"
    database_url_sync: str = "postgresql+psycopg2://storycards:storycards@db:5432/storycards"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Celery
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    # AI
    google_api_key: str = ""
    gemeni_model: str = "gemini-3-flash-preview"

    # HuggingFace
    hf_token: str = ""

    # Audio / TTS
    enable_audio_gen: bool = False
    sample_audio_url: str = "https://upload.wikimedia.org/wikipedia/commons/4/47/Sound_example.ogg"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
