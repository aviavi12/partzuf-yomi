import json
import logging
from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an analytical engine that classifies news events using a developmental metaphor framework.

IMPORTANT RULES:
1. You are NOT making scientific claims. You are using a developmental metaphor as an analytical framework.
2. Always separate FACT (what happened) from INTERPRETATION (what it might mean) from METAPHOR (the developmental analogy).
3. Never claim that a news event causes specific hormonal or neurological changes in any person.
4. When uncertain, mark confidence as low and claim_type as "speculation".
5. Present multiple interpretations when a political event is contested.

DEVELOPMENTAL STAGES (metaphorical):
- embryo: Dependency, infrastructure, vulnerability, environmental threats, survival, basic resources
- infant: Nurturing, regulation, care, attachment, protection, close environment
- child: Exploration, learning, imitation, boundaries, play, identity building, skill acquisition
- adult: Independence, responsibility, decisions, economy, leadership, self-defense
- first_woman: First significant encounter/relationship, self-discovery through the other, novelty
- primary_woman: Central relationship, commitment, home building, mutual responsibility, stability
- third_woman: Learning from previous relationships, transformation, maturity, new strategy
- courtship: Signaling, proposals, trust building, negotiation, small steps toward connection
- marriage: Agreement, covenant, signing, union, long-term cooperation, shared framework
- new_generation: Birth, new generation, future investment, demographic change, long-term education

EVENT TYPES: war, peace, alliance, economy, immigration, technology, family, elections, threat, defense, diplomacy, terrorism, security, education, health, birth, demography, energy, food, water, infrastructure, science, culture, religion, law, protest, leadership, negotiation, refugees, innovation, labor, cooperation, crisis, recovery, social_change

ISRAEL RELEVANCE:
- direct: Explicitly about Israel, Israeli entities, Jewish communities
- indirect: Affects Israel's security, economy, international relations, diaspora
- speculative: Possible but unsubstantiated connection (MUST be marked as such)
- none: No connection

Return ONLY valid JSON matching this schema:
{
  "event_type": "string",
  "developmental_stage": "string",
  "stage_score": 0-100,
  "israel_relevance": "direct|indirect|speculative|none",
  "israel_relevance_score": 0-100,
  "mother_analogy": {"score": 0-100, "interpretation": "string"},
  "father_analogy": {"score": 0-100, "interpretation": "string"},
  "son_perspective": {
    "what_is_happening": "string",
    "what_can_be_perceived": "string",
    "developmental_meaning": "string (MUST start with 'analytical hypothesis' if speculative)",
    "possible_long_term_pattern": "string",
    "certainty": 0.0-1.0
  },
  "scientific_context": {
    "evidence_level": "established|supported|plausible|speculative|metaphorical",
    "text": "string"
  },
  "confidence": 0.0-1.0,
  "reasoning_summary": "string"
}"""


async def analyze_article(headline: str, summary: str, source_name: str, language: str) -> dict:
    if not settings.ai_api_key:
        raise ValueError("AI API key not configured")

    client = AsyncOpenAI(api_key=settings.ai_api_key)

    user_prompt = f"""Analyze this news item:

Headline: {headline}
Summary: {summary}
Source: {source_name}
Language: {language}

Classify this event and return the JSON analysis."""

    try:
        response = await client.chat.completions.create(
            model=settings.ai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        result = json.loads(content)

        required_fields = ["event_type", "developmental_stage", "confidence"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field: {field}")

        result.setdefault("stage_score", 50)
        result.setdefault("israel_relevance", "none")
        result.setdefault("israel_relevance_score", 0)
        result.setdefault("mother_analogy", {"score": 0, "interpretation": ""})
        result.setdefault("father_analogy", {"score": 0, "interpretation": ""})
        result.setdefault("son_perspective", {
            "what_is_happening": headline,
            "what_can_be_perceived": "",
            "developmental_meaning": "",
            "possible_long_term_pattern": "",
            "certainty": 0.0,
        })
        result.setdefault("scientific_context", {
            "evidence_level": "metaphorical",
            "text": "",
        })
        result.setdefault("reasoning_summary", "")

        return result

    except json.JSONDecodeError as e:
        logger.error(f"AI returned invalid JSON: {e}")
        raise
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        raise
