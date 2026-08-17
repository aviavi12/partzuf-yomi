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

ISRAELI_RSS_FEEDS = [
    "https://www.ynet.co.il/Integration/StoryRss2.xml",
    "https://www.ynet.co.il/Integration/StoryRss1854.xml",
]


async def collect_rotter_news(db: AsyncSession) -> dict:
    source_map = await ensure_sources(db)
    source_id = source_map.get("rotter")
    if not source_id:
        return {"collected": 0, "duplicates": 0, "errors": ["Israeli source not found"]}

    collected = 0
    duplicates = 0
    errors = []

    seen_titles = set()

    for feed_url in ISRAELI_RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo and not feed.entries:
                logger.warning(f"Israeli feed unavailable: {feed_url}")
                errors.append(f"Feed unavailable: {feed_url}")
                continue

            for entry in feed.entries[:20]:
                headline = entry.get("title", "").strip()
                if not headline or len(headline) < 10:
                    continue

                if headline in seen_titles:
                    continue
                seen_titles.add(headline)

                summary = entry.get("summary", entry.get("description", "")).strip()
                link = entry.get("link", "")
                published = entry.get("published_parsed")
                pub_dt = datetime(*published[:6], tzinfo=pytz.utc) if published else datetime.now(tz)

                content_hash = hashlib.sha256(f"ynet:{headline}".encode()).hexdigest()

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
                    language="he",
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
