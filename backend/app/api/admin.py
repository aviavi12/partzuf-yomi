from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.system import TelegramMessage

router = APIRouter(prefix="/api/admin")


@router.get("/telegram-status")
async def telegram_status(db: AsyncSession = Depends(get_db)):
    from app.telegram.bot import _get_chat_ids
    chat_ids = _get_chat_ids()

    sent_count = 0
    last_sent = None
    if settings.telegram_bot_token and chat_ids:
        count_q = select(func.count()).select_from(TelegramMessage).where(TelegramMessage.status == "sent")
        result = await db.execute(count_q)
        sent_count = result.scalar() or 0

        last_q = select(TelegramMessage).where(TelegramMessage.status == "sent").order_by(TelegramMessage.created_at.desc()).limit(1)
        last_result = await db.execute(last_q)
        last_msg = last_result.scalar_one_or_none()
        if last_msg:
            last_sent = last_msg.sent_at.isoformat() if last_msg.sent_at else None

    return {
        "configured": bool(settings.telegram_bot_token and chat_ids),
        "bot_token_set": bool(settings.telegram_bot_token),
        "channels": {
            "default": bool(settings.telegram_chat_id),
            "global_הפרצוף_היומי": bool(settings.telegram_chat_id_global),
            "israel_הפרצוף_הזמני": bool(settings.telegram_chat_id_israel),
        },
        "active_chat_ids": list(chat_ids.keys()),
        "messages_sent": sent_count,
        "last_sent": last_sent,
    }


@router.post("/test-telegram")
async def test_telegram():
    if not settings.telegram_bot_token:
        raise HTTPException(status_code=400, detail="TELEGRAM_BOT_TOKEN must be set in .env")

    from app.telegram.bot import _get_chat_ids
    chat_ids = _get_chat_ids()
    if not chat_ids:
        raise HTTPException(status_code=400, detail="At least one TELEGRAM_CHAT_ID must be set in .env")

    try:
        import telegram
        bot = telegram.Bot(token=settings.telegram_bot_token)
        results = {}

        for channel, chat_id in chat_ids.items():
            if channel == "global":
                text = "🌍 <b>הפרצוף היומי</b> — בדיקת חיבור הצליחה!\n\nערוץ חדשות העולם מחובר ופעיל."
            elif channel == "israel":
                text = "🇮🇱 <b>הפרצוף הזמני</b> — בדיקת חיבור הצליחה!\n\nערוץ חדשות ישראל מחובר ופעיל."
            else:
                text = "✅ <b>Partzuf Yomi</b> — בדיקת חיבור טלגרם הצליחה!"

            sent = await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
            results[channel] = {"message_id": str(sent.message_id), "chat_id": chat_id}

        return {"status": "ok", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telegram error: {str(e)}")


@router.post("/run-collector")
async def run_collector(db: AsyncSession = Depends(get_db)):
    from app.services.pipeline import run_collection_pipeline
    try:
        result = await run_collection_pipeline(db)
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-analysis")
async def run_analysis(db: AsyncSession = Depends(get_db)):
    from app.services.pipeline import run_analysis_pipeline
    try:
        result = await run_analysis_pipeline(db)
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-telegram")
async def send_telegram(db: AsyncSession = Depends(get_db)):
    from app.services.pipeline import send_hourly_telegram
    try:
        result = await send_hourly_telegram(db)
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-synthesis")
async def run_synthesis(db: AsyncSession = Depends(get_db)):
    from app.services.daily_synthesis import generate_daily_synthesis
    try:
        result = await generate_daily_synthesis(db)
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full-pipeline")
async def full_pipeline(db: AsyncSession = Depends(get_db)):
    from app.services.pipeline import run_collection_pipeline, run_analysis_pipeline, send_hourly_telegram
    results = {}
    try:
        results["collection"] = await run_collection_pipeline(db)
        results["analysis"] = await run_analysis_pipeline(db)
        results["telegram"] = await send_hourly_telegram(db)
        return {"status": "ok", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
