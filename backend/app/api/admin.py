from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter(prefix="/api/admin")


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
