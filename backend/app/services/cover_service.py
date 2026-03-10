import httpx
from urllib.parse import quote
from loguru import logger


# Open Library Search API — free, no API key
OPEN_LIBRARY_SEARCH = "https://openlibrary.org/search.json"
OPEN_LIBRARY_COVER = "https://covers.openlibrary.org/b/olid/{}-L.jpg"


async def fetch_cover_url(title: str, author: str | None = None) -> str | None:
    """
    Search Open Library for a book/story and return its cover image URL.
    Works best for books; returns None if no cover is found.
    """
    try:
        params = {"q": title, "limit": 1, "fields": "cover_edition_key,edition_key,cover_i"}
        if author:
            params["author"] = author

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(OPEN_LIBRARY_SEARCH, params=params)
            resp.raise_for_status()
            data = resp.json()

        docs = data.get("docs", [])
        if not docs:
            logger.debug(f"No Open Library results for: {title}")
            return None

        doc = docs[0]

        # Prefer cover_i (direct cover ID) for the simplest URL
        cover_id = doc.get("cover_i")
        if cover_id:
            url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            logger.debug(f"Cover found for '{title}': {url}")
            return url

        # Fallback: use edition OLID
        olid = doc.get("cover_edition_key")
        if not olid:
            editions = doc.get("edition_key", [])
            olid = editions[0] if editions else None

        if olid:
            url = OPEN_LIBRARY_COVER.format(olid)
            logger.debug(f"Cover found for '{title}' (OLID): {url}")
            return url

        logger.debug(f"No cover available for: {title}")
        return None
    except Exception as e:
        logger.warning(f"Cover fetch failed for '{title}': {e}")
        return None
