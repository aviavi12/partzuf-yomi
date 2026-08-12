import logging
from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.database import async_session

logger = logging.getLogger(__name__)

tz = pytz.timezone(settings.timezone)

scheduler = AsyncIOScheduler(timezone=tz)


async def _hourly_job():
    logger.info("Running hourly collection + analysis + Telegram")
    async with async_session() as db:
        try:
            from app.services.pipeline import run_collection_pipeline, run_analysis_pipeline, send_hourly_telegram
            await run_collection_pipeline(db)
            await run_analysis_pipeline(db)
            await send_hourly_telegram(db)
        except Exception as e:
            logger.error(f"Hourly job error: {e}")


async def _daily_synthesis_job():
    logger.info("Running daily synthesis at 18:00")
    async with async_session() as db:
        try:
            from app.services.daily_synthesis import generate_daily_synthesis
            await generate_daily_synthesis(db)
        except Exception as e:
            logger.error(f"Daily synthesis error: {e}")


def start_scheduler():
    has_jobs = False

    if settings.hourly_collection_enabled:
        scheduler.add_job(
            _hourly_job,
            trigger=IntervalTrigger(hours=1),
            id="hourly_collection",
            name="Hourly News Collection & Analysis",
            replace_existing=True,
        )
        has_jobs = True
        logger.info("Hourly collection job enabled")
    else:
        logger.info("Hourly collection disabled by configuration")

    scheduler.add_job(
        _daily_synthesis_job,
        trigger=CronTrigger(hour=settings.daily_synthesis_hour, minute=0, timezone=tz),
        id="daily_synthesis",
        name=f"Daily Synthesis at {settings.daily_synthesis_hour}:00",
        replace_existing=True,
    )
    has_jobs = True
    logger.info(f"Daily synthesis job enabled at {settings.daily_synthesis_hour}:00 {settings.timezone}")

    if has_jobs:
        scheduler.start()
        logger.info("Scheduler started")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
