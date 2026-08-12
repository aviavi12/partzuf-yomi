import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.demo_data import load_demo_articles
from app.services.analysis_service import analyze_unprocessed_articles


@pytest.mark.asyncio
async def test_telegram_skipped_without_config(db):
    from app.telegram.bot import send_hourly_digest
    result = await send_hourly_digest(db)
    assert result["status"] == "skipped"
    assert "not configured" in result["reason"]


@pytest.mark.asyncio
async def test_telegram_skipped_no_articles(db):
    from app.telegram.bot import send_hourly_digest
    result = await send_hourly_digest(db)
    assert result["status"] == "skipped"


@pytest.mark.asyncio
async def test_daily_synthesis_no_articles(db):
    from app.services.daily_synthesis import generate_daily_synthesis
    result = await generate_daily_synthesis(db)
    assert result["status"] == "no_articles"


@pytest.mark.asyncio
async def test_daily_synthesis_with_data(db):
    await load_demo_articles(db)
    await analyze_unprocessed_articles(db)
    from app.services.daily_synthesis import generate_daily_synthesis
    result = await generate_daily_synthesis(db)
    assert result["status"] == "ok"
    assert result["total"] == 12
    assert result["dominant_stage"] is not None
