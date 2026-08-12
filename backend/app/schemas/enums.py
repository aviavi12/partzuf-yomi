from enum import Enum


class DevelopmentalStage(str, Enum):
    EMBRYO = "embryo"
    INFANT = "infant"
    CHILD = "child"
    ADULT = "adult"
    FIRST_WOMAN = "first_woman"
    PRIMARY_WOMAN = "primary_woman"
    THIRD_WOMAN = "third_woman"
    COURTSHIP = "courtship"
    MARRIAGE = "marriage"
    NEW_GENERATION = "new_generation"


STAGE_LABELS_HE = {
    DevelopmentalStage.EMBRYO: "עובר",
    DevelopmentalStage.INFANT: "יונק",
    DevelopmentalStage.CHILD: "ילד",
    DevelopmentalStage.ADULT: "בוגר",
    DevelopmentalStage.FIRST_WOMAN: "אישה ראשונה",
    DevelopmentalStage.PRIMARY_WOMAN: "אישה עיקרית",
    DevelopmentalStage.THIRD_WOMAN: "אישה שלישית",
    DevelopmentalStage.COURTSHIP: "חיזור",
    DevelopmentalStage.MARRIAGE: "נישואין",
    DevelopmentalStage.NEW_GENERATION: "דור חדש",
}

STAGE_ORDER = list(DevelopmentalStage)


class EventType(str, Enum):
    WAR = "war"
    PEACE = "peace"
    ALLIANCE = "alliance"
    ECONOMY = "economy"
    IMMIGRATION = "immigration"
    TECHNOLOGY = "technology"
    FAMILY = "family"
    ELECTIONS = "elections"
    THREAT = "threat"
    DEFENSE = "defense"
    DIPLOMACY = "diplomacy"
    TERRORISM = "terrorism"
    SECURITY = "security"
    EDUCATION = "education"
    HEALTH = "health"
    BIRTH = "birth"
    DEMOGRAPHY = "demography"
    ENERGY = "energy"
    FOOD = "food"
    WATER = "water"
    INFRASTRUCTURE = "infrastructure"
    SCIENCE = "science"
    CULTURE = "culture"
    RELIGION = "religion"
    LAW = "law"
    PROTEST = "protest"
    LEADERSHIP = "leadership"
    NEGOTIATION = "negotiation"
    REFUGEES = "refugees"
    INNOVATION = "innovation"
    LABOR = "labor"
    COOPERATION = "cooperation"
    CRISIS = "crisis"
    RECOVERY = "recovery"
    SOCIAL_CHANGE = "social_change"


EVENT_TYPE_LABELS_HE = {
    EventType.WAR: "מלחמה",
    EventType.PEACE: "שלום",
    EventType.ALLIANCE: "ברית",
    EventType.ECONOMY: "כלכלה",
    EventType.IMMIGRATION: "הגירה",
    EventType.TECHNOLOGY: "טכנולוגיה",
    EventType.FAMILY: "משפחה",
    EventType.ELECTIONS: "בחירות",
    EventType.THREAT: "איום",
    EventType.DEFENSE: "הגנה",
    EventType.DIPLOMACY: "דיפלומטיה",
    EventType.TERRORISM: "טרור",
    EventType.SECURITY: "ביטחון",
    EventType.EDUCATION: "חינוך",
    EventType.HEALTH: "בריאות",
    EventType.BIRTH: "ילודה",
    EventType.DEMOGRAPHY: "דמוגרפיה",
    EventType.ENERGY: "אנרגיה",
    EventType.FOOD: "מזון",
    EventType.WATER: "מים",
    EventType.INFRASTRUCTURE: "תשתיות",
    EventType.SCIENCE: "מדע",
    EventType.CULTURE: "תרבות",
    EventType.RELIGION: "דת",
    EventType.LAW: "משפט",
    EventType.PROTEST: "מחאה",
    EventType.LEADERSHIP: "מנהיגות",
    EventType.NEGOTIATION: "משא ומתן",
    EventType.REFUGEES: "פליטים",
    EventType.INNOVATION: "חדשנות",
    EventType.LABOR: "שוק העבודה",
    EventType.COOPERATION: "שיתוף פעולה",
    EventType.CRISIS: "משבר",
    EventType.RECOVERY: "התאוששות",
    EventType.SOCIAL_CHANGE: "שינוי חברתי",
}


class IsraelRelevanceType(str, Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    SPECULATIVE = "speculative"
    NONE = "none"


class ClaimType(str, Enum):
    FACT = "fact"
    INFERENCE = "inference"
    INTERPRETATION = "interpretation"
    SPECULATION = "speculation"
    METAPHOR = "metaphor"


class EvidenceLevel(str, Enum):
    ESTABLISHED = "established"
    SUPPORTED = "supported"
    PLAUSIBLE = "plausible"
    SPECULATIVE = "speculative"
    METAPHORICAL = "metaphorical"
