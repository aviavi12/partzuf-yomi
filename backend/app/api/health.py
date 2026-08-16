import logging
from datetime import datetime, timedelta

import pytz
from fastapi import APIRouter, BackgroundTasks
from sqlalchemy import select

router = APIRouter()
logger = logging.getLogger(__name__)

_last_catchup_check: datetime | None = None


async def _catchup_if_needed():
    global _last_catchup_check

    tz = pytz.timezone("Asia/Jerusalem")
    now = datetime.now(tz)

    if _last_catchup_check and (now - _last_catchup_check).total_seconds() < 1800:
        return
    _last_catchup_check = now

    try:
        from app.database import async_session
        from app.models.system import TelegramMessage

        async with async_session() as db:
            q = select(TelegramMessage).where(
                TelegramMessage.message_type == "hourly_unified",
                TelegramMessage.status == "sent",
            ).order_by(TelegramMessage.sent_at.desc()).limit(1)
            result = await db.execute(q)
            last_msg = result.scalar_one_or_none()

            should_run_hourly = True
            if last_msg and last_msg.sent_at:
                sent_at = last_msg.sent_at
                if sent_at.tzinfo is None:
                    sent_at = tz.localize(sent_at)
                elapsed = (now - sent_at).total_seconds()
                should_run_hourly = elapsed > 3300

            if should_run_hourly:
                logger.info("Catchup: running overdue hourly pipeline")
                from app.services.pipeline import (
                    run_collection_pipeline,
                    run_analysis_pipeline,
                    send_hourly_telegram,
                )
                await run_collection_pipeline(db)
                await run_analysis_pipeline(db)
                await send_hourly_telegram(db)

            if now.hour >= 18:
                today_start = tz.localize(
                    datetime.combine(now.date(), datetime.min.time())
                )
                q = select(TelegramMessage).where(
                    TelegramMessage.message_type == "daily_synthesis",
                    TelegramMessage.status == "sent",
                    TelegramMessage.sent_at >= today_start.replace(tzinfo=None),
                ).limit(1)
                result = await db.execute(q)
                has_daily = result.scalar_one_or_none()

                if not has_daily:
                    logger.info("Catchup: running overdue daily synthesis")
                    from app.services.daily_synthesis import generate_daily_synthesis
                    await generate_daily_synthesis(db)

    except Exception as e:
        logger.error(f"Catchup check failed: {e}")


@router.get("/health")
async def health_check(background_tasks: BackgroundTasks):
    background_tasks.add_task(_catchup_if_needed)
    return {
        "status": "ok",
        "service": "Israel News Developmental Analysis Engine",
        "version": "0.1.0",
    }
