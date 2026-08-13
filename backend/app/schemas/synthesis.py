from datetime import date, datetime
from pydantic import BaseModel


class DailyTrend(BaseModel):
    dominant_stage: str | None = None
    secondary_stage: str | None = None
    dominant_event_types: list[str] = []
    global_pattern: str = ""
    israel_pattern: str = ""
    father_pattern: str = ""
    mother_pattern: str = ""
    son_perspective: str = ""
    relationship_pattern: str = ""
    future_pattern: str = ""
    confidence: float = 0.0


class DailySummaryResponse(BaseModel):
    id: str
    summary_date: date
    total_articles: int
    global_articles: int
    israel_articles: int

    dominant_stage: str | None = None
    secondary_stage: str | None = None

    global_pattern: str | None = None
    israel_pattern: str | None = None
    father_pattern: str | None = None
    mother_pattern: str | None = None
    son_perspective: str | None = None
    relationship_pattern: str | None = None
    future_pattern: str | None = None

    daily_stage_vector_json: str | None = None
    temporal_analysis_json: str | None = None

    trend_text: str | None = None
    confidence: float = 0.0

    telegram_sent: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_articles_today: int = 0
    global_articles_today: int = 0
    israel_articles_today: int = 0
    avg_israel_relevance: float = 0.0
    dominant_stage: str | None = None
    dominant_stage_label_he: str | None = None
    avg_confidence: float = 0.0
    stage_distribution: dict[str, int] = {}
    event_type_distribution: dict[str, int] = {}
    israel_relevance_distribution: dict[str, int] = {}
