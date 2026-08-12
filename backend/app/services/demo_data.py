import hashlib
import uuid
from datetime import datetime, timedelta

import pytz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.news import NewsSource, NewsArticle

tz = pytz.timezone(settings.timezone)

DEMO_SOURCES = [
    {
        "name": "Associated Press",
        "slug": "ap",
        "url": "https://apnews.com/",
        "source_type": "international",
        "language": "en",
        "reliability_score": 0.9,
    },
    {
        "name": "Rotter",
        "slug": "rotter",
        "url": "https://rotter.net/",
        "source_type": "israeli",
        "language": "he",
        "reliability_score": 0.7,
    },
]

DEMO_ARTICLES = [
    {
        "source_slug": "ap",
        "headline": "UN Security Council holds emergency session on Middle East tensions",
        "summary": "The UN Security Council convened an emergency session to discuss escalating tensions in the Middle East, with multiple nations calling for diplomatic solutions.",
        "language": "en",
        "hours_ago": 1,
    },
    {
        "source_slug": "ap",
        "headline": "Global tech summit announces breakthrough in renewable energy storage",
        "summary": "Scientists at the Global Technology Summit presented a new battery technology that could revolutionize renewable energy storage, potentially reducing costs by 60%.",
        "language": "en",
        "hours_ago": 2,
    },
    {
        "source_slug": "ap",
        "headline": "International trade agreement signed between 12 Pacific nations",
        "summary": "Twelve Pacific nations signed a comprehensive trade agreement aimed at reducing tariffs and promoting economic cooperation across the region.",
        "language": "en",
        "hours_ago": 3,
    },
    {
        "source_slug": "ap",
        "headline": "WHO reports significant progress in global vaccination campaign",
        "summary": "The World Health Organization announced that its global vaccination initiative has reached 85% coverage in developing nations, marking a historic milestone.",
        "language": "en",
        "hours_ago": 4,
    },
    {
        "source_slug": "ap",
        "headline": "Major diplomatic talks resume between rival nations after two-year pause",
        "summary": "Diplomatic negotiations between two long-standing rival nations resumed after a two-year hiatus, with mediators expressing cautious optimism about potential agreements.",
        "language": "en",
        "hours_ago": 5,
    },
    {
        "source_slug": "rotter",
        "headline": "ממשלת ישראל מאשרת תקציב חדש לפיתוח תשתיות בנגב",
        "summary": "הממשלה אישרה תקציב של 2.5 מיליארד שקל לפיתוח תשתיות תחבורה, מים ואנרגיה באזור הנגב, במטרה לעודד התיישבות ופיתוח כלכלי.",
        "language": "he",
        "hours_ago": 1,
    },
    {
        "source_slug": "rotter",
        "headline": "צה\"ל מקיים תרגיל רב-זרועי בצפון הארץ",
        "summary": "צבא ההגנה לישראל ערך תרגיל צבאי רחב היקף בצפון הארץ, הכולל כוחות יבשה, אוויר וים, כהכנה לתרחישים ביטחוניים אפשריים.",
        "language": "he",
        "hours_ago": 2,
    },
    {
        "source_slug": "rotter",
        "headline": "עלייה חדה בהגירה לישראל מצרפת ומדרום אמריקה",
        "summary": "נתוני הסוכנות היהודית מראים עלייה של 40% בהגירה לישראל מצרפת ו-35% מדרום אמריקה ברבעון האחרון, על רקע חששות ביטחוניים וכלכליים.",
        "language": "he",
        "hours_ago": 3,
    },
    {
        "source_slug": "rotter",
        "headline": "סטארטאפ ישראלי מפתח טכנולוגיה חדשנית להתפלת מים",
        "summary": "חברת הייטק ישראלית הציגה טכנולוגיה חדשה להתפלת מים שמפחיתה את צריכת האנרגיה ב-50%, עם פוטנציאל ליצוא לאפריקה והמזרח התיכון.",
        "language": "he",
        "hours_ago": 4,
    },
    {
        "source_slug": "rotter",
        "headline": "משרד החינוך מכריז על רפורמה בתכנית הלימודים להיסטוריה",
        "summary": "משרד החינוך הכריז על רפורמה מקיפה בתכנית הלימודים להיסטוריה, עם דגש מוגבר על חינוך לדמוקרטיה, שיח בין-תרבותי והיכרות עם תולדות העם היהודי.",
        "language": "he",
        "hours_ago": 5,
    },
    {
        "source_slug": "ap",
        "headline": "Record birth rate decline reported across European nations",
        "summary": "A new demographic study reveals record-low birth rates across 15 European nations, raising concerns about aging populations and future workforce sustainability.",
        "language": "en",
        "hours_ago": 6,
    },
    {
        "source_slug": "rotter",
        "headline": "ישראל וירדן חותמות על הסכם שיתוף פעולה במים ואנרגיה",
        "summary": "ישראל וירדן חתמו על הסכם חדש לשיתוף פעולה בתחומי המים והאנרגיה הסולארית, הכולל הקמת מתקן התפלה משותף באזור ים המלח.",
        "language": "he",
        "hours_ago": 6,
    },
]


def _content_hash(headline: str, source_slug: str) -> str:
    return hashlib.sha256(f"{source_slug}:{headline}".encode()).hexdigest()


async def ensure_sources(db: AsyncSession) -> dict[str, uuid.UUID]:
    source_map = {}
    for src_data in DEMO_SOURCES:
        result = await db.execute(select(NewsSource).where(NewsSource.slug == src_data["slug"]))
        existing = result.scalar_one_or_none()
        if existing:
            source_map[src_data["slug"]] = existing.id
        else:
            source = NewsSource(**src_data)
            db.add(source)
            await db.flush()
            source_map[src_data["slug"]] = source.id
    await db.commit()
    return source_map


async def load_demo_articles(db: AsyncSession) -> int:
    source_map = await ensure_sources(db)
    now = datetime.now(tz)
    loaded = 0

    for article_data in DEMO_ARTICLES:
        content_hash = _content_hash(article_data["headline"], article_data["source_slug"])

        existing = await db.execute(select(NewsArticle).where(NewsArticle.content_hash == content_hash))
        if existing.scalar_one_or_none():
            continue

        article = NewsArticle(
            source_id=source_map[article_data["source_slug"]],
            headline=article_data["headline"],
            summary=article_data["summary"],
            language=article_data["language"],
            published_at=now - timedelta(hours=article_data["hours_ago"]),
            content_hash=content_hash,
            is_demo=True,
        )
        db.add(article)
        loaded += 1

    await db.commit()
    return loaded
