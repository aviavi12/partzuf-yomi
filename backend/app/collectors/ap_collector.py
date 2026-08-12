import hashlib
import logging
from datetime import datetime

import feedparser
import pytz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.news import NewsArticle, NewsSource
from app.services.demo_data import ensure_sources

logger = logging.getLogger(__name__)

tz = pytz.timezone(settings.timezone)

AP_RSS_FEEDS = [
    "https://rsshub.app/apnews/topics/world-news",
    "https://rsshub.app/apnews/topics/politics",
]


async def collect_ap_news(db: AsyncSession) -> dict:
    """
    Collect news from AP via publicly available RSS feeds.
    If no RSS feed is accessible, return an empty result.
    """
    source_map = await ensure_sources(db)
    source_id = source_map.get("ap")
    if not source_id:
        return {"collected": 0, "duplicates": 0, "errors": ["AP source not found"]}

    collected = 0
    duplicates = 0
    errors = []

    for feed_url in AP_RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo and not feed.entries:
                logger.warning(f"Feed unavailable or invalid: {feed_url}")
                errors.append(f"Feed unavailable: {feed_url}")
                continue

            for entry in feed.entries[:20]:
                headline = entry.get("title", "").strip()
                if not headline:
                    continue

                summary = entry.get("summary", entry.get("description", "")).strip()
                link = entry.get("link", "")
                published = entry.get("published_parsed")
                pub_dt = datetime(*published[:6], tzinfo=pytz.utc) if published else datetime.now(tz)

                content_hash = hashlib.sha256(f"ap:{headline}".encode()).hexdigest()

                existing = await db.execute(
                    select(NewsArticle).where(NewsArticle.content_hash == content_hash)
                )
                if existing.scalar_one_or_none():
                    duplicates += 1
                    continue

                article = NewsArticle(
                    source_id=source_id,
                    external_id=entry.get("id", link),
                    headline=headline,
                    summary=summary[:2000] if summary else None,
                    url=link,
                    language="en",
                    published_at=pub_dt,
                    content_hash=content_hash,
                    is_demo=False,
                )
                db.add(article)
                collected += 1

        except Exception as e:
            logger.error(f"Error collecting from {feed_url}: {e}")
            errors.append(str(e))

    if collected > 0:
        await db.commit()

    return {"collected": collected, "duplicates": duplicates, "errors": errors}
