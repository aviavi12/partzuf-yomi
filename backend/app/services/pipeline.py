import logging
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def run_collection_pipeline(db: AsyncSession) -> dict:
    logger.info("Starting collection pipeline")
    from app.config import settings

    results = {"collected": 0, "duplicates": 0, "errors": []}

    if settings.demo_mode:
        from app.services.demo_data import load_demo_articles
        count = await load_demo_articles(db)
        results["collected"] = count
        results["source"] = "demo"
        logger.info(f"Demo mode: loaded {count} articles")
    else:
        try:
            from app.collectors.ap_collector import collect_ap_news
            ap_result = await collect_ap_news(db)
            results["collected"] += ap_result.get("collected", 0)
            results["duplicates"] += ap_result.get("duplicates", 0)
        except Exception as e:
            logger.error(f"AP collector error: {e}")
            results["errors"].append(f"AP: {str(e)}")

        try:
            from app.collectors.rotter_collector import collect_rotter_news
            rotter_result = await collect_rotter_news(db)
            results["collected"] += rotter_result.get("collected", 0)
            results["duplicates"] += rotter_result.get("duplicates", 0)
        except Exception as e:
            logger.error(f"Rotter collector error: {e}")
            results["errors"].append(f"Rotter: {str(e)}")

    logger.info(f"Collection pipeline complete: {results}")
    return results


async def run_analysis_pipeline(db: AsyncSession) -> dict:
    logger.info("Starting analysis pipeline")
    from app.services.analysis_service import analyze_unprocessed_articles
    result = await analyze_unprocessed_articles(db)
    logger.info(f"Analysis pipeline complete: {result}")
    return result


async def send_hourly_telegram(db: AsyncSession) -> dict:
    logger.info("Sending hourly Telegram digest")
    from app.telegram.bot import send_hourly_digest
    result = await send_hourly_digest(db)
    return result
