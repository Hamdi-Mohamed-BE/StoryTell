import os
from datetime import timedelta

from loguru import logger

from app.config import get_settings


def setup_logging() -> logger:
    """Configure loguru sinks using app config. Call once at startup."""
    settings = get_settings()

    os.makedirs(settings.app_logs_dir, exist_ok=True)

    logger.remove()

    # Console sink
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level="DEBUG" if settings.debug else "INFO",
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    # File sink — warnings, errors, and success only
    logger.add(
        sink=os.path.join(settings.app_logs_dir, "logs.log"),
        level="DEBUG",
        filter=lambda record: record["level"].name in {"WARNING", "ERROR", "SUCCESS"},
        rotation=timedelta(days=1),
        retention=timedelta(days=7),
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )

    logger.info(f"Logging configured — logs dir: {os.path.abspath(settings.app_logs_dir)}")
    return logger
