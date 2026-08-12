import logging
from datetime import datetime, timedelta

import pytz
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.news import NewsArticle, NewsSource
from app.models.analysis import EventClassification, DevelopmentalAnalysis, IsraelRelevance
from app.models.system import TelegramMessage
from app.schemas.enums import STAGE_LABELS_HE, EVENT_TYPE_LABELS_HE, DevelopmentalStage, EventType

logger = logging.getLogger(__name__)

tz = pytz.timezone(settings.timezone)


async def send_hourly_digest(db: AsyncSession) -> dict:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning("Telegram not configured, skipping digest")
        return {"status": "skipped", "reason": "Telegram not configured"}

    now = datetime.now(tz)
    hour_ago = now - timedelta(hours=1)

    articles_q = select(NewsArticle).where(NewsArticle.collected_at >= hour_ago).order_by(NewsArticle.published_at.desc())
    result = await db.execute(articles_q)
    articles = result.scalars().all()

    if not articles:
        return {"status": "skipped", "reason": "No articles in the last hour"}

    global_articles = []
    israel_articles = []

    for article in articles:
        source_result = await db.execute(select(NewsSource).where(NewsSource.id == article.source_id))
        source = source_result.scalar_one_or_none()

        dev_result = await db.execute(select(DevelopmentalAnalysis).where(DevelopmentalAnalysis.article_id == article.id))
        dev = dev_result.scalar_one_or_none()

        isr_result = await db.execute(select(IsraelRelevance).where(IsraelRelevance.article_id == article.id))
        isr = isr_result.scalar_one_or_none()

        entry = {
            "headline": article.headline,
            "source": source.name if source else "?",
            "stage": dev.developmental_stage if dev else None,
            "confidence": dev.confidence if dev else 0,
            "israel_relevance": isr.relevance_type if isr else "none",
        }

        if source and source.source_type == "international":
            global_articles.append(entry)
        else:
            israel_articles.append(entry)

    stage_counts: dict[str, int] = {}
    for a in articles:
        dev_r = await db.execute(select(DevelopmentalAnalysis).where(DevelopmentalAnalysis.article_id == a.id))
        dev_obj = dev_r.scalar_one_or_none()
        if dev_obj:
            stage_counts[dev_obj.developmental_stage] = stage_counts.get(dev_obj.developmental_stage, 0) + 1

    dominant = max(stage_counts, key=stage_counts.get) if stage_counts else "unknown"
    try:
        dominant_he = STAGE_LABELS_HE.get(DevelopmentalStage(dominant), dominant)
    except ValueError:
        dominant_he = dominant

    message = _format_hourly_message(now, global_articles, israel_articles, dominant_he, stage_counts)

    try:
        import telegram
        bot = telegram.Bot(token=settings.telegram_bot_token)
        sent = await bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=message,
            parse_mode="HTML",
        )

        tg_msg = TelegramMessage(
            message_type="hourly_digest",
            content=message,
            telegram_message_id=str(sent.message_id),
            sent_at=now,
            status="sent",
        )
        db.add(tg_msg)
        await db.commit()

        return {"status": "sent", "message_id": str(sent.message_id)}

    except Exception as e:
        logger.error(f"Telegram send error: {e}")

        tg_msg = TelegramMessage(
            message_type="hourly_digest",
            content=message,
            status="failed",
            error=str(e),
        )
        db.add(tg_msg)
        await db.commit()

        return {"status": "error", "error": str(e)}


def _format_hourly_message(
    now: datetime,
    global_articles: list[dict],
    israel_articles: list[dict],
    dominant_stage_he: str,
    stage_counts: dict[str, int],
) -> str:
    time_str = now.strftime("%H:%M %d/%m/%Y")
    lines = [f"📰 <b>מבזק שעתי — {time_str}</b>", ""]

    if global_articles:
        lines.append("🌍 <b>העולם</b>")
        for a in global_articles[:5]:
            lines.append(f"• {a['headline'][:100]}")
        lines.append("")

    if israel_articles:
        lines.append("🇮🇱 <b>ישראל</b>")
        for a in israel_articles[:5]:
            lines.append(f"• {a['headline'][:100]}")
        lines.append("")

    lines.append(f"🧬 <b>שלב התפתחותי דומיננטי:</b> {dominant_stage_he}")
    lines.append("")

    lines.append("📊 <b>התפלגות שלבים:</b>")
    for stage_key, count in sorted(stage_counts.items(), key=lambda x: -x[1]):
        try:
            label = STAGE_LABELS_HE.get(DevelopmentalStage(stage_key), stage_key)
        except ValueError:
            label = stage_key
        lines.append(f"  {label}: {count}")
    lines.append("")

    lines.append("⚠️ <i>זהו מודל אנליטי מטפורי.</i>")
    lines.append("<i>אין לראות בו קביעה מדעית או רפואית.</i>")

    return "\n".join(lines)


async def send_daily_synthesis(db: AsyncSession, synthesis_text: str) -> dict:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return {"status": "skipped", "reason": "Telegram not configured"}

    try:
        import telegram
        bot = telegram.Bot(token=settings.telegram_bot_token)
        sent = await bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=synthesis_text,
            parse_mode="HTML",
        )

        tg_msg = TelegramMessage(
            message_type="daily_synthesis",
            content=synthesis_text,
            telegram_message_id=str(sent.message_id),
            sent_at=datetime.now(tz),
            status="sent",
        )
        db.add(tg_msg)
        await db.commit()

        return {"status": "sent", "message_id": str(sent.message_id)}

    except Exception as e:
        logger.error(f"Telegram daily synthesis error: {e}")
        return {"status": "error", "error": str(e)}
