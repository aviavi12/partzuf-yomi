import json
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news import NewsArticle, NewsSource
from app.models.analysis import EventClassification, DevelopmentalAnalysis, IsraelRelevance
from app.config import settings

logger = logging.getLogger(__name__)


async def analyze_unprocessed_articles(db: AsyncSession) -> dict:
    result = await db.execute(
        select(NewsArticle).where(NewsArticle.is_analyzed == False).limit(50)
    )
    articles = result.scalars().all()

    if not articles:
        return {"analyzed": 0, "message": "No unprocessed articles found"}

    analyzed = 0
    errors = []

    for article in articles:
        try:
            source_result = await db.execute(select(NewsSource).where(NewsSource.id == article.source_id))
            source = source_result.scalar_one_or_none()

            if settings.ai_provider != "none" and settings.ai_api_key:
                from app.analyzers.ai_analyzer import analyze_article
                ai_result = await analyze_article(
                    headline=article.headline,
                    summary=article.summary or "",
                    source_name=source.name if source else "unknown",
                    language=article.language,
                )
            else:
                from app.classifiers.rule_classifier import classify_article
                ai_result = classify_article(
                    headline=article.headline,
                    summary=article.summary or "",
                    source_name=source.name if source else "unknown",
                    language=article.language,
                )

            classification = EventClassification(
                article_id=article.id,
                event_type=ai_result["event_type"],
                confidence=ai_result["confidence"],
                claim_type="inference",
                reasoning=ai_result.get("reasoning_summary", ""),
            )
            db.add(classification)

            stage_scores = ai_result.get("stage_scores", {})
            causal_chain = ai_result.get("causal_chain", {})

            dev_analysis = DevelopmentalAnalysis(
                article_id=article.id,
                developmental_stage=ai_result["developmental_stage"],
                stage_score=ai_result["stage_score"],
                mother_analogy_score=ai_result.get("mother_analogy", {}).get("score", 0),
                mother_analogy_text=ai_result.get("mother_analogy", {}).get("interpretation", ""),
                father_analogy_score=ai_result.get("father_analogy", {}).get("score", 0),
                father_analogy_text=ai_result.get("father_analogy", {}).get("interpretation", ""),
                son_perspective_json=json.dumps(ai_result.get("son_perspective", {}), ensure_ascii=False),
                scientific_context_json=json.dumps(ai_result.get("scientific_context", {}), ensure_ascii=False),
                stage_vector_json=json.dumps(stage_scores, ensure_ascii=False),
                causal_chain_json=json.dumps(causal_chain, ensure_ascii=False),
                father_attributes_json=json.dumps(
                    ai_result.get("father_analogy", {}).get("attributes", {}), ensure_ascii=False
                ),
                mother_attributes_json=json.dumps(
                    ai_result.get("mother_analogy", {}).get("attributes", {}), ensure_ascii=False
                ),
                confidence=ai_result["confidence"],
                final_score=ai_result.get("final_score", _calculate_final_score(ai_result)),
                analysis_text=ai_result.get("reasoning_summary", ""),
                claim_type="interpretation",
            )
            db.add(dev_analysis)

            israel_mechanism = ai_result.get("israel_mechanism", {})
            israel_rel = IsraelRelevance(
                article_id=article.id,
                relevance_type=ai_result.get("israel_relevance", "none"),
                relevance_score=ai_result.get("israel_relevance_score", 0),
                explanation=israel_mechanism.get("mechanism", ai_result.get("reasoning_summary", "")),
                claim_type="inference",
            )
            db.add(israel_rel)

            article.is_analyzed = True
            analyzed += 1

        except Exception as e:
            logger.error(f"Error analyzing article {article.id}: {e}")
            errors.append({"article_id": str(article.id), "error": str(e)})

    await db.commit()
    return {"analyzed": analyzed, "errors": errors, "total_unprocessed": len(articles)}


def _calculate_final_score(ai_result: dict) -> int:
    base_weight = ai_result.get("stage_score", 50) / 100.0
    israel_relevance = ai_result.get("israel_relevance_score", 0) / 100.0
    confidence = ai_result.get("confidence", 0.5)
    source_reliability = 0.8
    evidence_strength = 0.6
    temporal_fit = 0.7
    relationship_fit = 0.6

    raw = (
        base_weight
        * evidence_strength
        * (0.3 + 0.7 * israel_relevance)
        * temporal_fit
        * relationship_fit
        * source_reliability
    ) * 100

    return max(0, min(100, int(raw)))
