import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class EventClassification(Base):
    __tablename__ = "event_classifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    article_id: Mapped[str] = mapped_column(String(36), ForeignKey("news_articles.id"), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    secondary_event_types: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    claim_type: Mapped[str] = mapped_column(String(50), default="inference")
    reasoning: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    article: Mapped["NewsArticle"] = relationship(back_populates="classification")


class DevelopmentalAnalysis(Base):
    __tablename__ = "developmental_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    article_id: Mapped[str] = mapped_column(String(36), ForeignKey("news_articles.id"), unique=True, nullable=False)

    developmental_stage: Mapped[str] = mapped_column(String(50), nullable=False)
    stage_score: Mapped[int] = mapped_column(Integer, default=0)

    mother_analogy_score: Mapped[int] = mapped_column(Integer, default=0)
    mother_analogy_text: Mapped[str | None] = mapped_column(Text)

    father_analogy_score: Mapped[int] = mapped_column(Integer, default=0)
    father_analogy_text: Mapped[str | None] = mapped_column(Text)

    son_perspective_json: Mapped[str | None] = mapped_column(Text)

    scientific_context_json: Mapped[str | None] = mapped_column(Text)

    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    final_score: Mapped[int] = mapped_column(Integer, default=0)
    analysis_text: Mapped[str | None] = mapped_column(Text)
    claim_type: Mapped[str] = mapped_column(String(50), default="interpretation")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    article: Mapped["NewsArticle"] = relationship(back_populates="developmental_analysis")

    @property
    def son_perspective(self) -> dict | None:
        if self.son_perspective_json:
            import json
            return json.loads(self.son_perspective_json)
        return None

    @son_perspective.setter
    def son_perspective(self, value: dict | None):
        if value is not None:
            import json
            self.son_perspective_json = json.dumps(value, ensure_ascii=False)
        else:
            self.son_perspective_json = None

    @property
    def scientific_context(self) -> dict | None:
        if self.scientific_context_json:
            import json
            return json.loads(self.scientific_context_json)
        return None

    @scientific_context.setter
    def scientific_context(self, value: dict | None):
        if value is not None:
            import json
            self.scientific_context_json = json.dumps(value, ensure_ascii=False)
        else:
            self.scientific_context_json = None


class IsraelRelevance(Base):
    __tablename__ = "israel_relevance"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    article_id: Mapped[str] = mapped_column(String(36), ForeignKey("news_articles.id"), unique=True, nullable=False)
    relevance_type: Mapped[str] = mapped_column(String(50), nullable=False)
    relevance_score: Mapped[int] = mapped_column(Integer, default=0)
    explanation: Mapped[str | None] = mapped_column(Text)
    entities_json: Mapped[str | None] = mapped_column(Text)
    claim_type: Mapped[str] = mapped_column(String(50), default="inference")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    article: Mapped["NewsArticle"] = relationship(back_populates="israel_relevance")
