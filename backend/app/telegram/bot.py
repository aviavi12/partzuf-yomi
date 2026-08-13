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


def _get_chat_ids() -> dict[str, str]:
    ids = {}
    if settings.telegram_chat_id_global:
        ids["global"] = settings.telegram_chat_id_global
    if settings.telegram_chat_id_israel:
        ids["israel"] = settings.telegram_chat_id_israel
    if not ids and settings.telegram_chat_id:
        ids["global"] = settings.telegram_chat_id
        ids["israel"] = settings.telegram_chat_id
    return ids


async def _send_message(bot, chat_id: str, text: str, db: AsyncSession, msg_type: str) -> dict:
    try:
        sent = await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
        )
        tg_msg = TelegramMessage(
            message_type=msg_type,
            content=text,
            telegram_message_id=str(sent.message_id),
            sent_at=datetime.now(tz),
            status="sent",
        )
        db.add(tg_msg)
        return {"status": "sent", "message_id": str(sent.message_id), "chat_id": chat_id}
    except Exception as e:
        logger.error(f"Telegram send error to {chat_id}: {e}")
        tg_msg = TelegramMessage(
            message_type=msg_type,
            content=text,
            status="failed",
            error=str(e),
        )
        db.add(tg_msg)
        return {"status": "error", "error": str(e), "chat_id": chat_id}


async def send_hourly_digest(db: AsyncSession) -> dict:
    if not settings.telegram_bot_token:
        logger.warning("Telegram bot token not configured, skipping digest")
        return {"status": "skipped", "reason": "Telegram not configured"}

    chat_ids = _get_chat_ids()
    if not chat_ids:
        logger.warning("No Telegram chat IDs configured, skipping digest")
        return {"status": "skipped", "reason": "No chat IDs configured"}

    now = datetime.now(tz)
    hour_ago_utc = datetime.utcnow() - timedelta(hours=1)

    articles_q = select(NewsArticle).where(NewsArticle.collected_at >= hour_ago_utc).order_by(NewsArticle.published_at.desc())
    result = await db.execute(articles_q)
    articles = result.scalars().all()

    if not articles:
        all_count_q = select(func.count()).select_from(NewsArticle)
        all_count = (await db.execute(all_count_q)).scalar() or 0
        if all_count > 0:
            articles_q = select(NewsArticle).where(NewsArticle.is_analyzed == True).order_by(NewsArticle.collected_at.desc()).limit(30)
            result = await db.execute(articles_q)
            articles = result.scalars().all()
        if not articles:
            return {"status": "skipped", "reason": "No articles found"}

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

    import telegram
    bot = telegram.Bot(token=settings.telegram_bot_token)
    results = {}

    if "global" in chat_ids and global_articles:
        msg = _format_global_message(now, global_articles, dominant_he, stage_counts)
        results["global"] = await _send_message(bot, chat_ids["global"], msg, db, "hourly_global")

    if "israel" in chat_ids and israel_articles:
        msg = _format_israel_message(now, israel_articles, dominant_he, stage_counts)
        results["israel"] = await _send_message(bot, chat_ids["israel"], msg, db, "hourly_israel")

    if not results:
        combined = _format_combined_message(now, global_articles, israel_articles, dominant_he, stage_counts)
        fallback_id = chat_ids.get("global") or chat_ids.get("israel")
        if fallback_id:
            results["combined"] = await _send_message(bot, fallback_id, combined, db, "hourly_digest")

    await db.commit()
    return {"status": "sent", "channels": results}


def _format_global_message(
    now: datetime,
    global_articles: list[dict],
    dominant_stage_he: str,
    stage_counts: dict[str, int],
) -> str:
    time_str = now.strftime("%H:%M %d/%m/%Y")
    lines = [f"🌍 <b>הפרצוף היומי — מבזק שעתי</b>", f"<i>{time_str}</i>", ""]

    lines.append("<b>חדשות העולם:</b>")
    for a in global_articles[:8]:
        stage_label = ""
        if a.get("stage"):
            try:
                stage_label = f" [{STAGE_LABELS_HE.get(DevelopmentalStage(a['stage']), a['stage'])}]"
            except ValueError:
                stage_label = f" [{a['stage']}]"
        lines.append(f"• {a['headline'][:120]}{stage_label}")
    lines.append("")

    lines.append(f"🧬 <b>שלב דומיננטי:</b> {dominant_stage_he}")
    lines.append("")

    lines.append("📊 <b>התפלגות:</b>")
    for stage_key, count in sorted(stage_counts.items(), key=lambda x: -x[1])[:5]:
        try:
            label = STAGE_LABELS_HE.get(DevelopmentalStage(stage_key), stage_key)
        except ValueError:
            label = stage_key
        lines.append(f"  {label}: {count}")
    lines.append("")

    lines.append("⚠️ <i>מודל אנליטי מטפורי — אין לראות בו קביעה מדעית.</i>")
    return "\n".join(lines)


def _format_israel_message(
    now: datetime,
    israel_articles: list[dict],
    dominant_stage_he: str,
    stage_counts: dict[str, int],
) -> str:
    time_str = now.strftime("%H:%M %d/%m/%Y")
    lines = [f"🇮🇱 <b>הפרצוף הזמני — מבזק שעתי</b>", f"<i>{time_str}</i>", ""]

    lines.append("<b>חדשות ישראל:</b>")
    for a in israel_articles[:8]:
        stage_label = ""
        if a.get("stage"):
            try:
                stage_label = f" [{STAGE_LABELS_HE.get(DevelopmentalStage(a['stage']), a['stage'])}]"
            except ValueError:
                stage_label = f" [{a['stage']}]"
        lines.append(f"• {a['headline'][:120]}{stage_label}")
    lines.append("")

    lines.append(f"🧬 <b>שלב דומיננטי:</b> {dominant_stage_he}")
    lines.append("")

    lines.append("📊 <b>התפלגות:</b>")
    for stage_key, count in sorted(stage_counts.items(), key=lambda x: -x[1])[:5]:
        try:
            label = STAGE_LABELS_HE.get(DevelopmentalStage(stage_key), stage_key)
        except ValueError:
            label = stage_key
        lines.append(f"  {label}: {count}")
    lines.append("")

    lines.append("⚠️ <i>מודל אנליטי מטפורי — אין לראות בו קביעה מדעית.</i>")
    return "\n".join(lines)


def _format_combined_message(
    now: datetime,
    global_articles: list[dict],
    israel_articles: list[dict],
    dominant_stage_he: str,
    stage_counts: dict[str, int],
) -> str:
    time_str = now.strftime("%H:%M %d/%m/%Y")
    lines = [f"📰 <b>מבזק שעתי — {time_str}</b>", ""]

    if global_articles:
        lines.append("🌍 <b>הפרצוף היומי — העולם</b>")
        for a in global_articles[:5]:
            lines.append(f"• {a['headline'][:100]}")
        lines.append("")

    if israel_articles:
        lines.append("🇮🇱 <b>הפרצוף הזמני — ישראל</b>")
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
    if not settings.telegram_bot_token:
        return {"status": "skipped", "reason": "Telegram not configured"}

    chat_ids = _get_chat_ids()
    if not chat_ids:
        return {"status": "skipped", "reason": "No chat IDs configured"}

    import telegram
    bot = telegram.Bot(token=settings.telegram_bot_token)
    results = {}

    for channel, chat_id in chat_ids.items():
        results[channel] = await _send_message(bot, chat_id, synthesis_text, db, f"daily_synthesis_{channel}")

    await db.commit()
    return {"status": "sent", "channels": results}
