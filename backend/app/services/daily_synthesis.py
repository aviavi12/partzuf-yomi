import json
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
from app.schemas.enums import STAGE_LABELS_HE, EVENT_TYPE_LABELS_HE, DevelopmentalStage, EventType, STAGE_ORDER

logger = logging.getLogger(__name__)

tz = pytz.timezone(settings.timezone)

ALL_STAGES = [s.value for s in DevelopmentalStage]


async def _load_all_day_articles(db: AsyncSession, day_start: datetime, day_end: datetime) -> list:
    q = select(NewsArticle).where(
        and_(NewsArticle.collected_at >= day_start, NewsArticle.collected_at <= day_end)
    ).order_by(NewsArticle.published_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


async def generate_daily_synthesis(db: AsyncSession, target_date: date | None = None) -> dict:
    target = target_date or date.today()
    day_start = datetime.combine(target, datetime.min.time())
    day_end = datetime.combine(target, datetime.max.time())

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
    stage_vectors = []

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
            if dev.stage_vector_json:
                try:
                    sv = json.loads(dev.stage_vector_json)
                    stage_vectors.append(sv)
                except (json.JSONDecodeError, TypeError):
                    pass

        isr_r = await db.execute(select(IsraelRelevance).where(IsraelRelevance.article_id == article.id))
        isr = isr_r.scalar_one_or_none()
        if isr:
            relevance_counter[isr.relevance_type] += 1

    dominant_stage = stage_counter.most_common(1)[0][0] if stage_counter else None
    secondary_stage = stage_counter.most_common(2)[1][0] if len(stage_counter) > 1 else None
    dominant_events = dict(event_counter.most_common(5))

    avg_mother = sum(mother_scores) / len(mother_scores) if mother_scores else 0
    avg_father = sum(father_scores) / len(father_scores) if father_scores else 0

    daily_stage_vector = _compute_daily_stage_vector(stage_vectors, stage_counter, total)

    yesterday = target - timedelta(days=1)
    temporal_analysis = await _temporal_analysis(db, target, yesterday, dominant_stage, daily_stage_vector)

    try:
        dom_he = STAGE_LABELS_HE.get(DevelopmentalStage(dominant_stage), dominant_stage) if dominant_stage else "?"
    except ValueError:
        dom_he = dominant_stage or "?"

    trend_text = _generate_trend_text(
        dom_he, dominant_stage, secondary_stage, dominant_events,
        global_count, israel_count, avg_mother, avg_father,
        daily_stage_vector, temporal_analysis,
    )

    confidence = min(1.0, total / 20.0) * 0.8

    existing = await db.execute(select(DailySummary).where(DailySummary.summary_date == target))
    summary = existing.scalar_one_or_none()

    stage_vector_str = json.dumps(daily_stage_vector, ensure_ascii=False)
    temporal_str = json.dumps(temporal_analysis, ensure_ascii=False)

    if summary:
        summary.total_articles = total
        summary.global_articles = global_count
        summary.israel_articles = israel_count
        summary.dominant_stage = dominant_stage
        summary.secondary_stage = secondary_stage
        summary.dominant_event_types_json = json.dumps(dominant_events, ensure_ascii=False)
        summary.stage_distribution_json = json.dumps(dict(stage_counter), ensure_ascii=False)
        summary.daily_stage_vector_json = stage_vector_str
        summary.temporal_analysis_json = temporal_str
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
            dominant_event_types_json=json.dumps(dominant_events, ensure_ascii=False),
            stage_distribution_json=json.dumps(dict(stage_counter), ensure_ascii=False),
            daily_stage_vector_json=stage_vector_str,
            temporal_analysis_json=temporal_str,
            trend_text=trend_text,
            confidence=confidence,
        )
        db.add(summary)

    await db.commit()

    from app.telegram.bot import _load_articles, _gather_analysis, _format_daily_full_analysis, send_daily_synthesis

    all_articles = await _load_all_day_articles(db, day_start, day_end)
    tg_data = await _gather_analysis(db, all_articles)

    date_str = target.strftime("%d/%m/%Y")
    tg_text = _format_daily_full_analysis(date_str, tg_data, trend_text)

    tg_result = await send_daily_synthesis(db, tg_text)

    if tg_result.get("status") == "sent":
        summary.telegram_sent = True
        await db.commit()

    return {
        "status": "ok",
        "date": str(target),
        "total": total,
        "dominant_stage": dominant_stage,
        "daily_stage_vector": daily_stage_vector,
        "temporal": temporal_analysis,
        "telegram": tg_result.get("status"),
    }


def _compute_daily_stage_vector(stage_vectors: list[dict], stage_counter: Counter, total: int) -> dict[str, float]:
    if stage_vectors:
        aggregated = {s: 0.0 for s in ALL_STAGES}
        for sv in stage_vectors:
            for stage, score in sv.items():
                if stage in aggregated:
                    aggregated[stage] += score
        n = len(stage_vectors)
        return {s: round(v / n, 3) for s, v in aggregated.items()}

    if total == 0:
        return {s: 0.0 for s in ALL_STAGES}
    return {s: round(stage_counter.get(s, 0) / total, 3) for s in ALL_STAGES}


async def _temporal_analysis(
    db: AsyncSession,
    today: date,
    yesterday: date,
    today_dominant: str | None,
    today_vector: dict[str, float],
) -> dict:
    yesterday_summary_r = await db.execute(
        select(DailySummary).where(DailySummary.summary_date == yesterday)
    )
    yesterday_summary = yesterday_summary_r.scalar_one_or_none()

    result = {
        "has_previous_day": False,
        "direction": "unknown",
        "regression_detected": False,
        "progression_detected": False,
        "stage_shift": None,
        "vector_delta": {},
    }

    if not yesterday_summary or not yesterday_summary.dominant_stage:
        return result

    result["has_previous_day"] = True
    prev_dominant = yesterday_summary.dominant_stage

    if prev_dominant == today_dominant:
        result["direction"] = "stable"
    else:
        try:
            prev_idx = ALL_STAGES.index(prev_dominant)
            curr_idx = ALL_STAGES.index(today_dominant) if today_dominant else prev_idx

            if curr_idx > prev_idx:
                result["direction"] = "progression"
                result["progression_detected"] = True
            elif curr_idx < prev_idx:
                result["direction"] = "regression"
                result["regression_detected"] = True

            result["stage_shift"] = {
                "from": prev_dominant,
                "to": today_dominant,
                "from_he": _stage_label_he(prev_dominant),
                "to_he": _stage_label_he(today_dominant),
            }
        except ValueError:
            result["direction"] = "unknown"

    if yesterday_summary.daily_stage_vector_json:
        try:
            prev_vector = json.loads(yesterday_summary.daily_stage_vector_json)
            delta = {}
            for stage in ALL_STAGES:
                prev_val = prev_vector.get(stage, 0.0)
                curr_val = today_vector.get(stage, 0.0)
                d = round(curr_val - prev_val, 3)
                if abs(d) > 0.01:
                    delta[stage] = d
            result["vector_delta"] = delta
        except (json.JSONDecodeError, TypeError):
            pass

    return result


def _stage_label_he(stage: str | None) -> str:
    if not stage:
        return "?"
    try:
        return STAGE_LABELS_HE.get(DevelopmentalStage(stage), stage)
    except ValueError:
        return stage


def _generate_trend_text(
    dom_he: str,
    dominant_stage: str | None,
    secondary_stage: str | None,
    dominant_events: dict,
    global_count: int,
    israel_count: int,
    avg_mother: float,
    avg_father: float,
    daily_vector: dict[str, float],
    temporal: dict,
) -> str:
    event_list = ", ".join(dominant_events.keys()) if dominant_events else "לא זוהו"

    lines = [
        f"המגמה היומית:",
        "",
        f"השלב ההתפתחותי הדומיננטי (מטפורי): {dom_he}",
        f"סוגי אירועים מובילים: {event_list}",
        "",
        f"חדשות עולמיות: {global_count} | חדשות ישראליות: {israel_count}",
        "",
        f"ציון שכבת האם הממוצע: {avg_mother:.0f}/100",
        f"ציון שכבת האב הממוצע: {avg_father:.0f}/100",
    ]

    if avg_father > avg_mother + 20:
        lines.append("")
        lines.append("(השערה אנליטית) הסביבה מתאפיינת יותר בדפוסי 'אב' — הגנה, גבולות, אסטרטגיה.")
    elif avg_mother > avg_father + 20:
        lines.append("")
        lines.append("(השערה אנליטית) הסביבה מתאפיינת יותר בדפוסי 'אם' — טיפוח, ויסות, קשר.")

    top_stages = sorted(daily_vector.items(), key=lambda x: -x[1])[:3]
    if top_stages and top_stages[0][1] > 0:
        lines.append("")
        lines.append("וקטור שלבים יומי (3 מובילים):")
        for s, v in top_stages:
            label = _stage_label_he(s)
            lines.append(f"  {label}: {v:.2f}")

    if temporal.get("has_previous_day"):
        lines.append("")
        direction = temporal.get("direction", "unknown")
        if direction == "regression":
            shift = temporal.get("stage_shift", {})
            lines.append(f"⚠️ רגרסיה: מעבר מ-{shift.get('from_he', '?')} ל-{shift.get('to_he', '?')}")
        elif direction == "progression":
            shift = temporal.get("stage_shift", {})
            lines.append(f"📈 התקדמות: מעבר מ-{shift.get('from_he', '?')} ל-{shift.get('to_he', '?')}")
        elif direction == "stable":
            lines.append("יציבות: השלב הדומיננטי לא השתנה מאתמול.")

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
    daily_vector: dict[str, float],
    temporal: dict,
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
    ]

    if temporal.get("has_previous_day"):
        lines.append("")
        direction = temporal.get("direction", "unknown")
        if direction == "regression":
            shift = temporal.get("stage_shift", {})
            lines.append(f"⚠️ <b>רגרסיה:</b> {shift.get('from_he', '?')} ← {shift.get('to_he', '?')}")
        elif direction == "progression":
            shift = temporal.get("stage_shift", {})
            lines.append(f"📈 <b>התקדמות:</b> {shift.get('from_he', '?')} → {shift.get('to_he', '?')}")
        elif direction == "stable":
            lines.append("📊 <b>יציבות:</b> השלב הדומיננטי נשמר מאתמול")

    top_stages = sorted(daily_vector.items(), key=lambda x: -x[1])[:3]
    if top_stages and top_stages[0][1] > 0:
        lines.append("")
        lines.append("📐 <b>וקטור יומי:</b>")
        for s, v in top_stages:
            label = _stage_label_he(s)
            bar = "█" * int(v * 10)
            lines.append(f"  {label}: {bar} {v:.2f}")

    lines += [
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


