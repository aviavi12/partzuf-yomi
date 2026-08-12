import logging
from datetime import datetime, date, timedelta
from collections import Counter

import pytz
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.news import NewsArticle, NewsSource
from app.models.analysis import EventClassification, DevelopmentalAnalysis, IsraelRelevance
from app.models.synthesis import DailySummary
from app.schemas.enums import STAGE_LABELS_HE, EVENT_TYPE_LABELS_HE, DevelopmentalStage, EventType

logger = logging.getLogger(__name__)

tz = pytz.timezone(settings.timezone)


async def generate_daily_synthesis(db: AsyncSession, target_date: date | None = None) -> dict:
    target = target_date or date.today()
    day_start = datetime.combine(target, datetime.min.time()).replace(tzinfo=tz)
    day_end = datetime.combine(target, datetime.max.time()).replace(tzinfo=tz)

    articles_q = select(NewsArticle).where(
        and_(NewsArticle.collected_at >= day_start, NewsArticle.collected_at <= day_end)
    )
    result = await db.execute(articles_q)
    articles = result.scalars().all()

    if not articles:
        return {"status": "no_articles", "date": str(target)}

    total = len(articles)
    global_count = 0
    israel_count = 0
    stage_counter = Counter()
    event_counter = Counter()
    relevance_counter = Counter()
    mother_scores = []
    father_scores = []

    for article in articles:
        source_r = await db.execute(select(NewsSource).where(NewsSource.id == article.source_id))
        source = source_r.scalar_one_or_none()
        if source and source.source_type == "international":
            global_count += 1
        else:
            israel_count += 1

        cls_r = await db.execute(select(EventClassification).where(EventClassification.article_id == article.id))
        cls = cls_r.scalar_one_or_none()
        if cls:
            event_counter[cls.event_type] += 1

        dev_r = await db.execute(select(DevelopmentalAnalysis).where(DevelopmentalAnalysis.article_id == article.id))
        dev = dev_r.scalar_one_or_none()
        if dev:
            stage_counter[dev.developmental_stage] += 1
            mother_scores.append(dev.mother_analogy_score)
            father_scores.append(dev.father_analogy_score)

        isr_r = await db.execute(select(IsraelRelevance).where(IsraelRelevance.article_id == article.id))
        isr = isr_r.scalar_one_or_none()
        if isr:
            relevance_counter[isr.relevance_type] += 1

    dominant_stage = stage_counter.most_common(1)[0][0] if stage_counter else None
    secondary_stage = stage_counter.most_common(2)[1][0] if len(stage_counter) > 1 else None
    dominant_events = dict(event_counter.most_common(5))

    avg_mother = sum(mother_scores) / len(mother_scores) if mother_scores else 0
    avg_father = sum(father_scores) / len(father_scores) if father_scores else 0

    try:
        dom_he = STAGE_LABELS_HE.get(DevelopmentalStage(dominant_stage), dominant_stage) if dominant_stage else "?"
    except ValueError:
        dom_he = dominant_stage or "?"

    trend_text = _generate_trend_text(
        dom_he, dominant_stage, secondary_stage, dominant_events,
        global_count, israel_count, avg_mother, avg_father,
    )

    confidence = min(1.0, total / 20.0) * 0.8

    existing = await db.execute(select(DailySummary).where(DailySummary.summary_date == target))
    summary = existing.scalar_one_or_none()

    if summary:
        summary.total_articles = total
        summary.global_articles = global_count
        summary.israel_articles = israel_count
        summary.dominant_stage = dominant_stage
        summary.secondary_stage = secondary_stage
        summary.dominant_event_types = dominant_events
        summary.stage_distribution = dict(stage_counter)
        summary.trend_text = trend_text
        summary.confidence = confidence
    else:
        summary = DailySummary(
            summary_date=target,
            total_articles=total,
            global_articles=global_count,
            israel_articles=israel_count,
            dominant_stage=dominant_stage,
            secondary_stage=secondary_stage,
            dominant_event_types=dominant_events,
            stage_distribution=dict(stage_counter),
            trend_text=trend_text,
            confidence=confidence,
        )
        db.add(summary)

    await db.commit()

    tg_text = _format_daily_telegram(target, total, global_count, israel_count,
                                      dom_he, dominant_events, trend_text, confidence)

    from app.telegram.bot import send_daily_synthesis
    tg_result = await send_daily_synthesis(db, tg_text)

    if tg_result.get("status") == "sent":
        summary.telegram_sent = True
        await db.commit()

    return {
        "status": "ok",
        "date": str(target),
        "total": total,
        "dominant_stage": dominant_stage,
        "telegram": tg_result.get("status"),
    }


def _generate_trend_text(
    dom_he: str,
    dominant_stage: str | None,
    secondary_stage: str | None,
    dominant_events: dict,
    global_count: int,
    israel_count: int,
    avg_mother: float,
    avg_father: float,
) -> str:
    event_list = ", ".join(dominant_events.keys()) if dominant_events else "לא זוהו"

    lines = [
        f"המגמה היומית:",
        f"",
        f"השלב ההתפתחותי הדומיננטי (מטפורי): {dom_he}",
        f"סוגי אירועים מובילים: {event_list}",
        f"",
        f"חדשות עולמיות: {global_count} | חדשות ישראליות: {israel_count}",
        f"",
        f"ציון שכבת האם הממוצע: {avg_mother:.0f}/100",
        f"ציון שכבת האב הממוצע: {avg_father:.0f}/100",
    ]

    if avg_father > avg_mother + 20:
        lines.append("")
        lines.append("(השערה אנליטית) הסביבה מתאפיינת יותר בדפוסי 'אב' — הגנה, גבולות, אסטרטגיה.")
    elif avg_mother > avg_father + 20:
        lines.append("")
        lines.append("(השערה אנליטית) הסביבה מתאפיינת יותר בדפוסי 'אם' — טיפוח, ויסות, קשר.")

    return "\n".join(lines)


def _format_daily_telegram(
    target: date,
    total: int,
    global_count: int,
    israel_count: int,
    dom_he: str,
    dominant_events: dict,
    trend_text: str,
    confidence: float,
) -> str:
    date_str = target.strftime("%d/%m/%Y")

    event_labels = []
    for et in list(dominant_events.keys())[:3]:
        try:
            event_labels.append(EVENT_TYPE_LABELS_HE.get(EventType(et), et))
        except ValueError:
            event_labels.append(et)

    lines = [
        f"🧬 <b>סיכום יומי — {date_str}</b>",
        "",
        f"📊 סה\"כ אירועים: {total}",
        f"🌍 עולמי: {global_count} | 🇮🇱 ישראלי: {israel_count}",
        "",
        f"📈 <b>השלב הדומיננטי:</b> {dom_he}",
        f"🎯 <b>אירועים מובילים:</b> {', '.join(event_labels)}",
        "",
        f"🔬 <b>רמת ודאות:</b> {confidence:.0%}",
        "",
        "━━━━━━━━━━━━",
        "",
        trend_text,
        "",
        "━━━━━━━━━━━━",
        "",
        "⚠️ <i>זהו מודל אנליטי מטפורי — אין לראות בו קביעה מדעית או רפואית.</i>",
    ]

    return "\n".join(lines)
