"""
CLI command to trigger story generation and data migration.

Usage (from within the backend container):
    uv run python -m app.cli generate "Harry Potter and the Philosopher's Stone"
    uv run python -m app.cli generate "Breaking Bad" --type show --author "Vince Gilligan"
    uv run python -m app.cli generate "Attack on Titan" --type anime --description "Humanity fights Titans"
    uv run python -m app.cli migrate-media
Run inside docker:
    docker exec -it stroytell-api-1 uv run python -m app.cli generate "Harry Potter and the Philosopher's Stone"
    docker exec -it stroytell-api-1 uv run python -m app.cli migrate-media
"""

import argparse
import base64
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from loguru import logger

from app.config import get_settings
from app.models import Story, StorySection, StoryGenerationJob
from app.services.cover_service import fetch_cover_url
from app.services import media_service
from app.workers.tasks import generate_story_sections


def get_sync_session() -> Session:
    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    return Session(engine)


def cmd_generate(args: argparse.Namespace) -> None:
    """Check if story exists, create if not, then trigger AI pipeline."""
    session = get_sync_session()
    try:
        # Look up story by title (case-insensitive)
        story = session.execute(
            select(Story).where(Story.title.ilike(args.title))
        ).scalar_one_or_none()

        if story:
            logger.info(f"Story '{story.title}' already exists (uid={story.uid})")
        else:
            # Fetch cover image synchronously via httpx
            import httpx
            cover_image = None
            try:
                title_query = args.title.replace(" ", "+")
                url = f"https://openlibrary.org/search.json?q={title_query}&limit=1"
                resp = httpx.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    docs = data.get("docs", [])
                    if docs and docs[0].get("cover_i"):
                        cover_id = docs[0]["cover_i"]
                        cover_image = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            except Exception:
                logger.debug("Could not fetch cover image, continuing without one")

            story = Story(
                title=args.title,
                story_type=args.type,
                author=args.author,
                description=args.description,
                cover_image=cover_image,
            )
            session.add(story)
            session.commit()
            session.refresh(story)
            logger.info(f"Created story '{story.title}' (uid={story.uid})")

        # Create a generation job
        job = StoryGenerationJob(
            story_id=story.id,
            status="pending",
            total_sections=0,  # AI will decide
        )
        session.add(job)
        session.commit()
        session.refresh(job)

        logger.info(f"Created generation job (uid={job.uid}), dispatching to Celery...")

        # Dispatch to Celery worker
        generate_story_sections.delay(story.id, job.id)

        logger.info(f"Job dispatched! The worker will generate story cards asynchronously.")
        logger.info(f"Track progress at the web UI or check the jobs table.")

    finally:
        session.close()


def cmd_migrate_media(args: argparse.Namespace) -> None:
    """Migrate old base64 data-URL media to file-based storage."""
    session = get_sync_session()
    try:
        sections = session.execute(select(StorySection)).scalars().all()

        migrated_images = 0
        migrated_audio = 0
        skipped = 0

        for section in sections:
            changed = False

            # Migrate image if it's a base64 data URL
            if section.image_url and section.image_url.startswith("data:"):
                image_bytes = _decode_data_url(section.image_url)
                if image_bytes:
                    new_url = media_service.save_image(
                        section.story_id, section.section_index, image_bytes,
                    )
                    section.image_url = new_url
                    changed = True
                    migrated_images += 1
                    logger.debug(f"Section {section.id}: migrated image ({len(image_bytes)} bytes)")
                else:
                    logger.warning(f"Section {section.id}: failed to decode image data URL")

            # Migrate audio if it's a base64 data URL
            if section.audio_url and section.audio_url.startswith("data:"):
                audio_bytes = _decode_data_url(section.audio_url)
                if audio_bytes:
                    new_url = media_service.save_audio(
                        section.story_id, section.section_index, audio_bytes,
                    )
                    section.audio_url = new_url
                    changed = True
                    migrated_audio += 1
                    logger.debug(f"Section {section.id}: migrated audio ({len(audio_bytes)} bytes)")
                else:
                    logger.warning(f"Section {section.id}: failed to decode audio data URL")

            if not changed:
                skipped += 1

        session.commit()
        logger.info(
            f"Migration complete: {migrated_images} images, {migrated_audio} audio files migrated, "
            f"{skipped} sections skipped (already migrated or no media)"
        )
    finally:
        session.close()


def _decode_data_url(data_url: str) -> bytes | None:
    """Extract raw bytes from a data URL like 'data:image/png;base64,iVBOR...'."""
    try:
        # Format: data:[<mediatype>][;base64],<data>
        _, encoded = data_url.split(",", 1)
        return base64.b64decode(encoded)
    except Exception as e:
        logger.error(f"Failed to decode data URL: {e}")
        return None


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="storycards",
        description="StoryCards CLI — trigger AI story card generation",
    )
    subparsers = parser.add_subparsers(dest="command")

    gen_parser = subparsers.add_parser("generate", help="Generate story cards for a story")
    gen_parser.add_argument("title", help="Story title (e.g. 'Harry Potter and the Philosopher\\'s Stone')")
    gen_parser.add_argument("--type", default="book", choices=["book", "movie", "anime", "show"],
                            help="Story type (default: book)")
    gen_parser.add_argument("--author", default=None, help="Author or director")
    gen_parser.add_argument("--description", default=None, help="Brief description of the story")

    # migrate-media subcommand
    subparsers.add_parser("migrate-media", help="Migrate old base64 data-URL media to file-based storage")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "migrate-media":
        cmd_migrate_media(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
