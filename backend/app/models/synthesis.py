import uuid
from datetime import datetime, date

from sqlalchemy import String, Text, DateTime, Float, Integer, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class DailySummary(Base):
    __tablename__ = "daily_summaries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    summary_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    total_articles: Mapped[int] = mapped_column(Integer, default=0)
    global_articles: Mapped[int] = mapped_column(Integer, default=0)
    israel_articles: Mapped[int] = mapped_column(Integer, default=0)

    dominant_stage: Mapped[str | None] = mapped_column(String(50))
    secondary_stage: Mapped[str | None] = mapped_column(String(50))
    dominant_event_types_json: Mapped[str | None] = mapped_column(Text)
    stage_distribution_json: Mapped[str | None] = mapped_column(Text)

    global_pattern: Mapped[str | None] = mapped_column(Text)
    israel_pattern: Mapped[str | None] = mapped_column(Text)
    father_pattern: Mapped[str | None] = mapped_column(Text)
    mother_pattern: Mapped[str | None] = mapped_column(Text)
    son_perspective: Mapped[str | None] = mapped_column(Text)
    relationship_pattern: Mapped[str | None] = mapped_column(Text)
    future_pattern: Mapped[str | None] = mapped_column(Text)

    trend_text: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)

    telegram_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
