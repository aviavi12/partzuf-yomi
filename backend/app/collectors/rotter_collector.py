import hashlib
import logging
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
import pytz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.news import NewsArticle, NewsSource
from app.services.demo_data import ensure_sources

logger = logging.getLogger(__name__)

tz = pytz.timezone(settings.timezone)

ROTTER_HEADLINES_URL = "https://rotter.net/scoopscache.html"


async def collect_rotter_news(db: AsyncSession) -> dict:
    """
    Collect publicly visible headlines from Rotter's news ticker page.
    This accesses only the public-facing headlines page.
    No authentication bypass, CAPTCHA solving, or terms-of-service violation is performed.
    """
    source_map = await ensure_sources(db)
    source_id = source_map.get("rotter")
    if not source_id:
        return {"collected": 0, "duplicates": 0, "errors": ["Rotter source not found"]}

    collected = 0
    duplicates = 0
    errors = []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                ROTTER_HEADLINES_URL,
                headers={"User-Agent": "PartzufYomi/1.0 (news-aggregator)"},
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml", from_encoding="windows-1255")

            links = soup.find_all("a")
            for link in links:
                headline = link.get_text(strip=True)
                if not headline or len(headline) < 10:
                    continue

                href = link.get("href", "")
                if href and not href.startswith("http"):
                    href = f"https://rotter.net/{href}"

                content_hash = hashlib.sha256(f"rotter:{headline}".encode()).hexdigest()

                existing = await db.execute(
                    select(NewsArticle).where(NewsArticle.content_hash == content_hash)
                )
                if existing.scalar_one_or_none():
                    duplicates += 1
                    continue

                article = NewsArticle(
                    source_id=source_id,
                    headline=headline,
                    url=href if href else None,
                    language="he",
                    published_at=datetime.now(tz),
                    content_hash=content_hash,
                    is_demo=False,
                )
                db.add(article)
                collected += 1

        if collected > 0:
            await db.commit()

    except httpx.HTTPStatusError as e:
        logger.error(f"Rotter HTTP error: {e}")
        errors.append(f"HTTP {e.response.status_code}")
    except Exception as e:
        logger.error(f"Rotter collection error: {e}")
        errors.append(str(e))

    return {"collected": collected, "duplicates": duplicates, "errors": errors}
