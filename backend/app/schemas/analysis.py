from datetime import datetime
from pydantic import BaseModel

from app.schemas.enums import EvidenceLevel


class SonPerspective(BaseModel):
    what_is_happening: str = ""
    what_can_be_perceived: str = ""
    developmental_meaning: str = ""
    possible_long_term_pattern: str = ""
    certainty: float = 0.0


class ScientificContext(BaseModel):
    evidence_level: str = "metaphorical"
    text: str = ""


class AnalogyDetail(BaseModel):
    score: int = 0
    interpretation: str = ""


class AIAnalysisResult(BaseModel):
    event_type: str
    developmental_stage: str
    stage_score: int = 0
    israel_relevance: str = "none"
    israel_relevance_score: int = 0
    mother_analogy: AnalogyDetail = AnalogyDetail()
    father_analogy: AnalogyDetail = AnalogyDetail()
    son_perspective: SonPerspective = SonPerspective()
    scientific_context: ScientificContext = ScientificContext()
    confidence: float = 0.0
    reasoning_summary: str = ""


class FullAnalysisResponse(BaseModel):
    article_id: str
    headline: str
    source_name: str | None = None
    url: str | None = None
    published_at: datetime | None = None

    event_type: str | None = None
    event_type_label_he: str | None = None

    developmental_stage: str | None = None
    stage_label_he: str | None = None
    stage_score: int = 0

    israel_relevance_type: str | None = None
    israel_relevance_score: int = 0

    mother_analogy_score: int = 0
    mother_analogy_text: str | None = None

    father_analogy_score: int = 0
    father_analogy_text: str | None = None

    son_perspective: SonPerspective | None = None

    scientific_context: ScientificContext | None = None

    confidence: float = 0.0
    final_score: int = 0
    claim_type: str = "interpretation"

    model_config = {"from_attributes": True}
