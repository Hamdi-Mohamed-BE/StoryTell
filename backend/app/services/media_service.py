"""
Media storage service — saves generated files to disk.

Files are stored under MEDIA_DIR with the structure:
    media/stories/{story_id}/sections/{section_index}/image.png
    media/stories/{story_id}/sections/{section_index}/audio.mp3

Returns URL paths like /media/stories/42/sections/3/image.png
that get served by FastAPI's StaticFiles mount.

To migrate to cloud buckets later, swap this service's save/delete
methods to upload to S3/GCS instead of writing to the local filesystem.
"""

import os
from pathlib import Path
from loguru import logger

from app.config import get_settings


def _media_root() -> Path:
    return Path(get_settings().media_dir)


def save_image(story_id: int, section_index: int, image_bytes: bytes) -> str:
    """Save image bytes to disk. Returns the URL path (e.g. /media/stories/42/sections/1/image.png)."""
    rel_path = f"stories/{story_id}/sections/{section_index}/image.png"
    _write(rel_path, image_bytes)
    return f"/media/{rel_path}"


def save_audio(story_id: int, section_index: int, audio_bytes: bytes) -> str:
    """Save audio bytes to disk. Returns the URL path (e.g. /media/stories/42/sections/1/audio.mp3)."""
    rel_path = f"stories/{story_id}/sections/{section_index}/audio.mp3"
    _write(rel_path, audio_bytes)
    return f"/media/{rel_path}"


def _write(rel_path: str, data: bytes) -> None:
    """Write bytes to a file under the media root, creating directories as needed."""
    full_path = _media_root() / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(data)
    logger.debug(f"Saved media file: {full_path} ({len(data)} bytes)")
