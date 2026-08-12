import pytest
from app.services.demo_data import load_demo_articles, ensure_sources
from app.services.analysis_service import analyze_unprocessed_articles


@pytest.mark.asyncio
async def test_demo_data_loads(db):
    count = await load_demo_articles(db)
    assert count == 12


@pytest.mark.asyncio
async def test_demo_data_deduplication(db):
    first = await load_demo_articles(db)
    second = await load_demo_articles(db)
    assert first == 12
    assert second == 0


@pytest.mark.asyncio
async def test_sources_created(db):
    source_map = await ensure_sources(db)
    assert "ap" in source_map
    assert "rotter" in source_map


@pytest.mark.asyncio
async def test_analysis_pipeline(db):
    await load_demo_articles(db)
    result = await analyze_unprocessed_articles(db)
    assert result["analyzed"] == 12
    assert len(result.get("errors", [])) == 0


@pytest.mark.asyncio
async def test_news_api(client, db):
    await load_demo_articles(db)
    await analyze_unprocessed_articles(db)
    response = await client.get("/api/news")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 12
    assert len(data["items"]) == 12


@pytest.mark.asyncio
async def test_news_filter_by_source(client, db):
    await load_demo_articles(db)
    response = await client.get("/api/news?source=rotter")
    assert response.status_code == 200
    data = response.json()
    assert all(item["source_name"] == "Rotter" for item in data["items"])


@pytest.mark.asyncio
async def test_dashboard_api(client, db):
    await load_demo_articles(db)
    await analyze_unprocessed_articles(db)
    response = await client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_articles_today"] == 12
    assert data["global_articles_today"] == 6
    assert data["israel_articles_today"] == 6
    assert data["dominant_stage"] is not None
    assert len(data["stage_distribution"]) > 0


@pytest.mark.asyncio
async def test_analysis_api(client, db):
    await load_demo_articles(db)
    await analyze_unprocessed_articles(db)
    news_response = await client.get("/api/news")
    article_id = news_response.json()["items"][0]["id"]
    response = await client.get(f"/api/analysis/{article_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["event_type"] is not None
    assert data["developmental_stage"] is not None
    assert data["confidence"] > 0


@pytest.mark.asyncio
async def test_stages_api(client):
    response = await client.get("/api/stages")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    assert data[0]["value"] == "embryo"
    assert data[0]["label_he"] == "עובר"


@pytest.mark.asyncio
async def test_event_types_api(client):
    response = await client.get("/api/event-types")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 35


@pytest.mark.asyncio
async def test_404_article(client):
    response = await client.get("/api/news/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_daily_summary_empty(client):
    response = await client.get("/api/daily-summary")
    assert response.status_code == 200
