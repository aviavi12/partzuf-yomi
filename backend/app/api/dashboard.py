from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
import pytz

from app.database import get_db
from app.config import settings
from app.models.news import NewsArticle, NewsSource
from app.models.analysis import EventClassification, DevelopmentalAnalysis, IsraelRelevance
from app.models.synthesis import DailySummary
from app.schemas.synthesis import DashboardStats, DailySummaryResponse
from app.schemas.enums import STAGE_LABELS_HE, DevelopmentalStage

router = APIRouter(prefix="/api")

tz = pytz.timezone(settings.timezone)


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    now = datetime.now(tz)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_q = select(func.count(NewsArticle.id)).where(NewsArticle.collected_at >= today_start)
    total = (await db.execute(total_q)).scalar() or 0

    global_src = await db.execute(select(NewsSource.id).where(NewsSource.slug == "ap"))
    global_ids = [r[0] for r in global_src.all()]

    global_count = 0
    if global_ids:
        gc_q = select(func.count(NewsArticle.id)).where(
            and_(NewsArticle.collected_at >= today_start, NewsArticle.source_id.in_(global_ids))
        )
        global_count = (await db.execute(gc_q)).scalar() or 0

    israel_count = total - global_count

    avg_rel_q = (
        select(func.avg(IsraelRelevance.relevance_score))
        .select_from(IsraelRelevance)
        .join(NewsArticle, NewsArticle.id == IsraelRelevance.article_id)
        .where(NewsArticle.collected_at >= today_start)
    )
    avg_rel = (await db.execute(avg_rel_q)).scalar() or 0.0

    stage_q = (
        select(DevelopmentalAnalysis.developmental_stage, func.count(DevelopmentalAnalysis.id))
        .select_from(DevelopmentalAnalysis)
        .join(NewsArticle, NewsArticle.id == DevelopmentalAnalysis.article_id)
        .where(NewsArticle.collected_at >= today_start)
        .group_by(DevelopmentalAnalysis.developmental_stage)
    )
    stage_rows = (await db.execute(stage_q)).all()
    stage_dist = {row[0]: row[1] for row in stage_rows}

    dominant = max(stage_dist, key=stage_dist.get) if stage_dist else None
    dominant_he = None
    if dominant:
        try:
            dominant_he = STAGE_LABELS_HE.get(DevelopmentalStage(dominant))
        except ValueError:
            dominant_he = dominant

    event_q = (
        select(EventClassification.event_type, func.count(EventClassification.id))
        .select_from(EventClassification)
        .join(NewsArticle, NewsArticle.id == EventClassification.article_id)
        .where(NewsArticle.collected_at >= today_start)
        .group_by(EventClassification.event_type)
    )
    event_rows = (await db.execute(event_q)).all()
    event_dist = {row[0]: row[1] for row in event_rows}

    rel_q = (
        select(IsraelRelevance.relevance_type, func.count(IsraelRelevance.id))
        .select_from(IsraelRelevance)
        .join(NewsArticle, NewsArticle.id == IsraelRelevance.article_id)
        .where(NewsArticle.collected_at >= today_start)
        .group_by(IsraelRelevance.relevance_type)
    )
    rel_rows = (await db.execute(rel_q)).all()
    rel_dist = {row[0]: row[1] for row in rel_rows}

    avg_conf_q = (
        select(func.avg(DevelopmentalAnalysis.confidence))
        .select_from(DevelopmentalAnalysis)
        .join(NewsArticle, NewsArticle.id == DevelopmentalAnalysis.article_id)
        .where(NewsArticle.collected_at >= today_start)
    )
    avg_conf = (await db.execute(avg_conf_q)).scalar() or 0.0

    return DashboardStats(
        total_articles_today=total,
        global_articles_today=global_count,
        israel_articles_today=israel_count,
        avg_israel_relevance=round(avg_rel, 1),
        dominant_stage=dominant,
        dominant_stage_label_he=dominant_he,
        avg_confidence=round(avg_conf, 2),
        stage_distribution=stage_dist,
        event_type_distribution=event_dist,
        israel_relevance_distribution=rel_dist,
    )


@router.get("/daily-summary", response_model=DailySummaryResponse | None)
async def get_daily_summary(
    summary_date: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    target_date = summary_date or date.today()
    result = await db.execute(select(DailySummary).where(DailySummary.summary_date == target_date))
    summary = result.scalar_one_or_none()
    if not summary:
        return None
    return DailySummaryResponse.model_validate(summary)


@router.get("/stages")
async def list_stages():
    return [
        {"value": stage.value, "label_he": STAGE_LABELS_HE[stage], "order": i}
        for i, stage in enumerate(DevelopmentalStage)
    ]


@router.get("/event-types")
async def list_event_types():
    from app.schemas.enums import EVENT_TYPE_LABELS_HE, EventType
    return [
        {"value": et.value, "label_he": EVENT_TYPE_LABELS_HE[et]}
        for et in EventType
    ]
