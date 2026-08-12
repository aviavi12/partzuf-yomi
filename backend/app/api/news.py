import json
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.news import NewsArticle, NewsSource
from app.models.analysis import EventClassification, DevelopmentalAnalysis, IsraelRelevance
from app.schemas.news import NewsArticleResponse, NewsArticleListResponse
from app.schemas.analysis import FullAnalysisResponse, SonPerspective, ScientificContext
from app.schemas.enums import STAGE_LABELS_HE, EVENT_TYPE_LABELS_HE, DevelopmentalStage, EventType

router = APIRouter(prefix="/api")


@router.get("/news", response_model=NewsArticleListResponse)
async def list_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source: str | None = None,
    event_type: str | None = None,
    stage: str | None = None,
    relevance: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(NewsArticle)

    if source:
        src_q = await db.execute(select(NewsSource.id).where(NewsSource.slug == source))
        src_ids = [r[0] for r in src_q.all()]
        if src_ids:
            query = query.where(NewsArticle.source_id.in_(src_ids))

    if event_type:
        cls_q = await db.execute(
            select(EventClassification.article_id).where(EventClassification.event_type == event_type)
        )
        cls_ids = [r[0] for r in cls_q.all()]
        query = query.where(NewsArticle.id.in_(cls_ids))

    if stage:
        dev_q = await db.execute(
            select(DevelopmentalAnalysis.article_id).where(DevelopmentalAnalysis.developmental_stage == stage)
        )
        dev_ids = [r[0] for r in dev_q.all()]
        query = query.where(NewsArticle.id.in_(dev_ids))

    if relevance:
        rel_q = await db.execute(
            select(IsraelRelevance.article_id).where(IsraelRelevance.relevance_type == relevance)
        )
        rel_ids = [r[0] for r in rel_q.all()]
        query = query.where(NewsArticle.id.in_(rel_ids))

    if date_from:
        query = query.where(NewsArticle.published_at >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.where(NewsArticle.published_at <= datetime.combine(date_to, datetime.max.time()))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(NewsArticle.published_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    articles = result.scalars().all()

    items = []
    for article in articles:
        source_result = await db.execute(select(NewsSource).where(NewsSource.id == article.source_id))
        source_obj = source_result.scalar_one_or_none()
        items.append(
            NewsArticleResponse(
                id=article.id,
                source_id=article.source_id,
                source_name=source_obj.name if source_obj else None,
                external_id=article.external_id,
                headline=article.headline,
                summary=article.summary,
                content=article.content,
                url=article.url,
                language=article.language,
                published_at=article.published_at,
                collected_at=article.collected_at,
                content_hash=article.content_hash,
                is_demo=article.is_demo,
                is_analyzed=article.is_analyzed,
                cluster_id=article.cluster_id,
                created_at=article.created_at,
            )
        )

    return NewsArticleListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/news/{article_id}", response_model=NewsArticleResponse)
async def get_news_article(article_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NewsArticle).where(NewsArticle.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    source_result = await db.execute(select(NewsSource).where(NewsSource.id == article.source_id))
    source_obj = source_result.scalar_one_or_none()

    return NewsArticleResponse(
        id=article.id,
        source_id=article.source_id,
        source_name=source_obj.name if source_obj else None,
        external_id=article.external_id,
        headline=article.headline,
        summary=article.summary,
        content=article.content,
        url=article.url,
        language=article.language,
        published_at=article.published_at,
        collected_at=article.collected_at,
        content_hash=article.content_hash,
        is_demo=article.is_demo,
        is_analyzed=article.is_analyzed,
        cluster_id=article.cluster_id,
        created_at=article.created_at,
    )


@router.get("/analysis/{article_id}", response_model=FullAnalysisResponse)
async def get_analysis(article_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NewsArticle).where(NewsArticle.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    source_result = await db.execute(select(NewsSource).where(NewsSource.id == article.source_id))
    source_obj = source_result.scalar_one_or_none()

    cls_result = await db.execute(select(EventClassification).where(EventClassification.article_id == article_id))
    classification = cls_result.scalar_one_or_none()

    dev_result = await db.execute(select(DevelopmentalAnalysis).where(DevelopmentalAnalysis.article_id == article_id))
    dev_analysis = dev_result.scalar_one_or_none()

    isr_result = await db.execute(select(IsraelRelevance).where(IsraelRelevance.article_id == article_id))
    isr_rel = isr_result.scalar_one_or_none()

    event_type_val = classification.event_type if classification else None
    event_type_label_he = None
    if event_type_val:
        try:
            event_type_label_he = EVENT_TYPE_LABELS_HE.get(EventType(event_type_val))
        except ValueError:
            event_type_label_he = event_type_val

    stage = dev_analysis.developmental_stage if dev_analysis else None
    stage_label_he = None
    if stage:
        try:
            stage_label_he = STAGE_LABELS_HE.get(DevelopmentalStage(stage))
        except ValueError:
            stage_label_he = stage

    son_persp = None
    sci_ctx = None
    if dev_analysis:
        sp = dev_analysis.son_perspective
        if sp:
            son_persp = SonPerspective(**sp)
        sc = dev_analysis.scientific_context
        if sc:
            sci_ctx = ScientificContext(**sc)

    return FullAnalysisResponse(
        article_id=article.id,
        headline=article.headline,
        source_name=source_obj.name if source_obj else None,
        url=article.url,
        published_at=article.published_at,
        event_type=event_type_val,
        event_type_label_he=event_type_label_he,
        developmental_stage=stage,
        stage_label_he=stage_label_he,
        stage_score=dev_analysis.stage_score if dev_analysis else 0,
        israel_relevance_type=isr_rel.relevance_type if isr_rel else None,
        israel_relevance_score=isr_rel.relevance_score if isr_rel else 0,
        mother_analogy_score=dev_analysis.mother_analogy_score if dev_analysis else 0,
        mother_analogy_text=dev_analysis.mother_analogy_text if dev_analysis else None,
        father_analogy_score=dev_analysis.father_analogy_score if dev_analysis else 0,
        father_analogy_text=dev_analysis.father_analogy_text if dev_analysis else None,
        son_perspective=son_persp,
        scientific_context=sci_ctx,
        confidence=dev_analysis.confidence if dev_analysis else 0.0,
        final_score=dev_analysis.final_score if dev_analysis else 0,
        claim_type=dev_analysis.claim_type if dev_analysis else "interpretation",
    )
