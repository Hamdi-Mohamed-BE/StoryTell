from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models import Story

# Pre-loaded stories for testing — add/remove as needed
SEED_STORIES = [
    {
        "title": "Harry Potter and the Philosopher's Stone",
        "story_type": "book",
        "author": "J.K. Rowling",
        "description": "An orphaned boy discovers he is a wizard and attends Hogwarts School of Witchcraft and Wizardry.",
        "cover_image": "https://covers.openlibrary.org/b/id/10521270-L.jpg",
    },
    {
        "title": "The Lord of the Rings: The Fellowship of the Ring",
        "story_type": "book",
        "author": "J.R.R. Tolkien",
        "description": "A hobbit named Frodo inherits a powerful ring and must journey to destroy it before the Dark Lord Sauron reclaims it.",
        "cover_image": "https://covers.openlibrary.org/b/id/14627766-L.jpg",
    },
    {
        "title": "Attack on Titan",
        "story_type": "anime",
        "author": "Hajime Isayama",
        "description": "Humanity lives behind massive walls to protect themselves from giant humanoid Titans that devour people.",
        "cover_image": "https://covers.openlibrary.org/b/id/8483051-L.jpg",
    },
    {
        "title": "Breaking Bad",
        "story_type": "show",
        "author": "Vince Gilligan",
        "description": "A high school chemistry teacher turned methamphetamine producer partners with a former student.",
        "cover_image": "https://covers.openlibrary.org/b/id/8314134-L.jpg",
    },
    {
        "title": "Inception",
        "story_type": "movie",
        "author": "Christopher Nolan",
        "description": "A thief who steals secrets through dream-sharing technology is given the task of planting an idea into a CEO's mind.",
        "cover_image": "https://covers.openlibrary.org/b/id/8769348-L.jpg",
    },
    {
        "title": "1984",
        "story_type": "book",
        "author": "George Orwell",
        "description": "In a dystopian future, a man struggles against an omnipresent government that controls every aspect of life.",
        "cover_image": "https://covers.openlibrary.org/b/id/14845537-L.jpg",
    },
    {
        "title": "Spirited Away",
        "story_type": "anime",
        "author": "Hayao Miyazaki",
        "description": "A young girl enters a mysterious world of spirits and must work in a bathhouse to free herself and her parents.",
        "cover_image": "https://covers.openlibrary.org/b/id/9255480-L.jpg",
    },
    {
        "title": "The Great Gatsby",
        "story_type": "book",
        "author": "F. Scott Fitzgerald",
        "description": "A mysterious millionaire throws lavish parties in 1920s New York, driven by his obsession with a lost love.",
        "cover_image": "https://covers.openlibrary.org/b/id/14350216-L.jpg",
    },
]


async def seed_stories(session: AsyncSession) -> None:
    """Insert seed stories if the table is empty. Idempotent — skips if data exists."""
    result = await session.execute(select(Story).limit(1))
    if result.scalar_one_or_none() is not None:
        logger.info("Stories table already has data — skipping seed")
        return

    for data in SEED_STORIES:
        story = Story(**data)
        session.add(story)

    await session.commit()
    logger.info(f"Seeded {len(SEED_STORIES)} stories for testing")
