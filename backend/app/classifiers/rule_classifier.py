import re


KEYWORD_RULES = {
    "war": {
        "keywords_en": ["war", "military", "attack", "bomb", "strike", "combat", "troops", "invasion", "battle"],
        "keywords_he": ["מלחמה", "צבא", "תקיפה", "הפצצה", "לחימה", "כוחות", "פלישה", "קרב"],
        "default_stage": "embryo",
        "secondary_stages": ["adult"],
        "weight": 0.9,
    },
    "peace": {
        "keywords_en": ["peace", "ceasefire", "truce", "peace agreement", "reconciliation"],
        "keywords_he": ["שלום", "הפסקת אש", "הסכם שלום", "פיוס"],
        "default_stage": "marriage",
        "secondary_stages": ["courtship"],
        "weight": 0.85,
    },
    "alliance": {
        "keywords_en": ["alliance", "partnership", "cooperation", "agreement", "treaty", "pact"],
        "keywords_he": ["ברית", "שותפות", "שיתוף פעולה", "הסכם", "אמנה"],
        "default_stage": "primary_woman",
        "secondary_stages": ["marriage", "courtship"],
        "weight": 0.8,
    },
    "economy": {
        "keywords_en": ["economy", "economic", "trade", "market", "gdp", "inflation", "recession", "growth"],
        "keywords_he": ["כלכלה", "כלכלי", "סחר", "שוק", "תל\"ג", "אינפלציה", "מיתון", "צמיחה"],
        "default_stage": "adult",
        "secondary_stages": ["child"],
        "weight": 0.7,
    },
    "immigration": {
        "keywords_en": ["immigration", "migration", "immigrant", "asylum", "refugee", "aliyah"],
        "keywords_he": ["הגירה", "מהגרים", "עלייה", "פליטים", "מקלט"],
        "default_stage": "embryo",
        "secondary_stages": ["infant"],
        "weight": 0.75,
    },
    "technology": {
        "keywords_en": ["technology", "tech", "ai", "startup", "innovation", "digital", "cyber"],
        "keywords_he": ["טכנולוגיה", "הייטק", "סטארטאפ", "חדשנות", "דיגיטלי", "סייבר"],
        "default_stage": "child",
        "secondary_stages": ["new_generation"],
        "weight": 0.7,
    },
    "family": {
        "keywords_en": ["family", "birth", "fertility", "marriage", "children", "parenthood"],
        "keywords_he": ["משפחה", "ילודה", "פריון", "נישואין", "ילדים", "הורות"],
        "default_stage": "new_generation",
        "secondary_stages": ["infant", "marriage"],
        "weight": 0.8,
    },
    "elections": {
        "keywords_en": ["election", "vote", "ballot", "campaign", "parliament", "coalition"],
        "keywords_he": ["בחירות", "הצבעה", "קלפי", "קמפיין", "כנסת", "קואליציה"],
        "default_stage": "adult",
        "secondary_stages": ["child"],
        "weight": 0.75,
    },
    "threat": {
        "keywords_en": ["threat", "danger", "risk", "warning", "alert", "crisis"],
        "keywords_he": ["איום", "סכנה", "סיכון", "אזהרה", "התרעה", "משבר"],
        "default_stage": "embryo",
        "secondary_stages": ["infant"],
        "weight": 0.85,
    },
    "defense": {
        "keywords_en": ["defense", "security", "protect", "shield", "iron dome", "intelligence"],
        "keywords_he": ["הגנה", "ביטחון", "מגן", "כיפת ברזל", "מודיעין"],
        "default_stage": "embryo",
        "secondary_stages": ["adult"],
        "weight": 0.85,
    },
    "diplomacy": {
        "keywords_en": ["diplomacy", "diplomatic", "ambassador", "embassy", "foreign minister", "summit"],
        "keywords_he": ["דיפלומטיה", "דיפלומטי", "שגריר", "שגרירות", "שר החוץ", "פסגה"],
        "default_stage": "courtship",
        "secondary_stages": ["adult", "primary_woman"],
        "weight": 0.75,
    },
    "terrorism": {
        "keywords_en": ["terror", "terrorism", "terrorist", "hamas", "hezbollah", "attack"],
        "keywords_he": ["טרור", "מחבל", "חמאס", "חיזבאללה", "פיגוע"],
        "default_stage": "embryo",
        "secondary_stages": ["infant"],
        "weight": 0.95,
    },
    "security": {
        "keywords_en": ["security", "national security", "border", "surveillance"],
        "keywords_he": ["ביטחון", "ביטחון לאומי", "גבול", "מעקב"],
        "default_stage": "adult",
        "secondary_stages": ["embryo"],
        "weight": 0.8,
    },
    "education": {
        "keywords_en": ["education", "school", "university", "curriculum", "students", "teachers"],
        "keywords_he": ["חינוך", "בית ספר", "אוניברסיטה", "תכנית לימודים", "תלמידים", "מורים"],
        "default_stage": "child",
        "secondary_stages": ["new_generation"],
        "weight": 0.7,
    },
    "health": {
        "keywords_en": ["health", "hospital", "medical", "vaccine", "disease", "pandemic", "who"],
        "keywords_he": ["בריאות", "בית חולים", "רפואי", "חיסון", "מחלה", "מגפה"],
        "default_stage": "infant",
        "secondary_stages": ["embryo"],
        "weight": 0.75,
    },
    "birth": {
        "keywords_en": ["birth rate", "natality", "newborn", "fertility rate", "population growth"],
        "keywords_he": ["ילודה", "שיעור פריון", "יילוד", "גידול אוכלוסייה"],
        "default_stage": "new_generation",
        "secondary_stages": ["embryo"],
        "weight": 0.85,
    },
    "demography": {
        "keywords_en": ["demography", "population", "census", "aging", "demographic"],
        "keywords_he": ["דמוגרפיה", "אוכלוסייה", "מפקד", "הזדקנות", "דמוגרפי"],
        "default_stage": "new_generation",
        "secondary_stages": ["adult"],
        "weight": 0.7,
    },
    "energy": {
        "keywords_en": ["energy", "oil", "gas", "solar", "nuclear", "renewable"],
        "keywords_he": ["אנרגיה", "נפט", "גז", "סולארי", "גרעיני", "מתחדשת"],
        "default_stage": "embryo",
        "secondary_stages": ["adult"],
        "weight": 0.7,
    },
    "food": {
        "keywords_en": ["food", "agriculture", "famine", "hunger", "crop"],
        "keywords_he": ["מזון", "חקלאות", "רעב", "יבול"],
        "default_stage": "infant",
        "secondary_stages": ["embryo"],
        "weight": 0.75,
    },
    "water": {
        "keywords_en": ["water", "desalination", "drought", "water supply"],
        "keywords_he": ["מים", "התפלה", "בצורת", "אספקת מים"],
        "default_stage": "embryo",
        "secondary_stages": ["infant"],
        "weight": 0.75,
    },
    "infrastructure": {
        "keywords_en": ["infrastructure", "construction", "road", "railway", "bridge", "transport"],
        "keywords_he": ["תשתיות", "בנייה", "כביש", "רכבת", "גשר", "תחבורה"],
        "default_stage": "embryo",
        "secondary_stages": ["child"],
        "weight": 0.7,
    },
    "science": {
        "keywords_en": ["science", "research", "discovery", "laboratory", "experiment"],
        "keywords_he": ["מדע", "מחקר", "גילוי", "מעבדה", "ניסוי"],
        "default_stage": "child",
        "secondary_stages": ["new_generation"],
        "weight": 0.65,
    },
    "culture": {
        "keywords_en": ["culture", "art", "music", "film", "heritage", "tradition"],
        "keywords_he": ["תרבות", "אמנות", "מוזיקה", "קולנוע", "מורשת", "מסורת"],
        "default_stage": "child",
        "secondary_stages": ["adult"],
        "weight": 0.6,
    },
    "religion": {
        "keywords_en": ["religion", "religious", "faith", "prayer", "temple", "mosque", "church", "synagogue"],
        "keywords_he": ["דת", "דתי", "אמונה", "תפילה", "מקדש", "מסגד", "כנסייה", "בית כנסת"],
        "default_stage": "infant",
        "secondary_stages": ["adult"],
        "weight": 0.65,
    },
    "law": {
        "keywords_en": ["law", "court", "judge", "legal", "legislation", "supreme court"],
        "keywords_he": ["משפט", "בית משפט", "שופט", "חוק", "חקיקה", "בג\"ץ"],
        "default_stage": "adult",
        "secondary_stages": ["child"],
        "weight": 0.7,
    },
    "protest": {
        "keywords_en": ["protest", "demonstration", "rally", "strike", "civil unrest"],
        "keywords_he": ["מחאה", "הפגנה", "עצרת", "שביתה"],
        "default_stage": "adult",
        "secondary_stages": ["child"],
        "weight": 0.7,
    },
    "leadership": {
        "keywords_en": ["leader", "leadership", "president", "prime minister", "government"],
        "keywords_he": ["מנהיגות", "מנהיג", "נשיא", "ראש ממשלה", "ממשלה"],
        "default_stage": "adult",
        "secondary_stages": ["first_woman"],
        "weight": 0.75,
    },
    "negotiation": {
        "keywords_en": ["negotiation", "talks", "mediation", "dialogue", "proposal"],
        "keywords_he": ["משא ומתן", "שיחות", "תיווך", "דיאלוג", "הצעה"],
        "default_stage": "courtship",
        "secondary_stages": ["marriage"],
        "weight": 0.8,
    },
    "refugees": {
        "keywords_en": ["refugee", "displaced", "asylum seeker", "humanitarian"],
        "keywords_he": ["פליטים", "עקורים", "מבקשי מקלט", "הומניטרי"],
        "default_stage": "infant",
        "secondary_stages": ["embryo"],
        "weight": 0.8,
    },
    "innovation": {
        "keywords_en": ["innovation", "breakthrough", "revolutionary", "pioneer"],
        "keywords_he": ["חדשנות", "פריצת דרך", "מהפכני", "חלוץ"],
        "default_stage": "child",
        "secondary_stages": ["new_generation"],
        "weight": 0.7,
    },
    "labor": {
        "keywords_en": ["employment", "jobs", "labor", "unemployment", "workforce"],
        "keywords_he": ["תעסוקה", "משרות", "עבודה", "אבטלה", "כוח אדם"],
        "default_stage": "adult",
        "secondary_stages": ["child"],
        "weight": 0.65,
    },
    "cooperation": {
        "keywords_en": ["cooperation", "joint", "bilateral", "multilateral", "collaboration"],
        "keywords_he": ["שיתוף פעולה", "משותף", "דו-צדדי", "רב-צדדי"],
        "default_stage": "primary_woman",
        "secondary_stages": ["courtship", "marriage"],
        "weight": 0.75,
    },
    "crisis": {
        "keywords_en": ["crisis", "emergency", "collapse", "disaster", "catastrophe"],
        "keywords_he": ["משבר", "חירום", "קריסה", "אסון", "קטסטרופה"],
        "default_stage": "embryo",
        "secondary_stages": ["infant"],
        "weight": 0.9,
    },
    "recovery": {
        "keywords_en": ["recovery", "reconstruction", "rebuilding", "rehabilitation"],
        "keywords_he": ["התאוששות", "שיקום", "בנייה מחדש", "שיקום"],
        "default_stage": "third_woman",
        "secondary_stages": ["adult"],
        "weight": 0.7,
    },
    "social_change": {
        "keywords_en": ["social change", "reform", "equality", "rights", "inclusion"],
        "keywords_he": ["שינוי חברתי", "רפורמה", "שוויון", "זכויות", "הכלה"],
        "default_stage": "child",
        "secondary_stages": ["new_generation"],
        "weight": 0.7,
    },
}

ISRAEL_KEYWORDS = {
    "direct": [
        "israel", "israeli", "ישראל", "ישראלי", "idf", "צה\"ל", "jerusalem", "ירושלים",
        "tel aviv", "תל אביב", "knesset", "כנסת", "netanyahu", "נתניהו",
        "jewish", "יהודי", "יהודים", "zionist", "ציוני", "mossad", "מוסד",
        "shin bet", "שב\"כ", "gaza", "עזה", "west bank", "גדה",
    ],
    "indirect": [
        "middle east", "מזרח התיכון", "iran", "איראן", "hezbollah", "חיזבאללה",
        "hamas", "חמאס", "lebanon", "לבנון", "syria", "סוריה",
        "antisemitism", "אנטישמיות", "jewish community", "קהילה יהודית",
        "abraham accords", "הסכמי אברהם", "diaspora", "תפוצות",
    ],
}


def classify_article(headline: str, summary: str, source_name: str, language: str) -> dict:
    text = f"{headline} {summary}".lower()
    scores: dict[str, float] = {}

    for event_type, rules in KEYWORD_RULES.items():
        keywords = rules["keywords_en"] + rules["keywords_he"]
        match_count = sum(1 for kw in keywords if kw.lower() in text)
        if match_count > 0:
            scores[event_type] = match_count * rules["weight"]

    if not scores:
        event_type = "security"
        stage = "adult"
        weight = 0.3
    else:
        event_type = max(scores, key=scores.get)
        stage = KEYWORD_RULES[event_type]["default_stage"]
        weight = KEYWORD_RULES[event_type]["weight"]

    israel_type, israel_score = _classify_israel_relevance(text)

    confidence = min(1.0, weight * 0.8 + (0.2 if israel_score > 50 else 0))

    stage_score = int(weight * 100)

    return {
        "event_type": event_type,
        "developmental_stage": stage,
        "stage_score": stage_score,
        "israel_relevance": israel_type,
        "israel_relevance_score": israel_score,
        "mother_analogy": _mother_analogy(stage, event_type),
        "father_analogy": _father_analogy(stage, event_type),
        "son_perspective": _son_perspective(stage, event_type, headline),
        "scientific_context": {
            "evidence_level": "metaphorical",
            "text": "Classification based on keyword rule matching. This is an analytical framework, not a scientific claim.",
        },
        "confidence": confidence,
        "reasoning_summary": f"Rule-based classification: {event_type} -> {stage} (confidence: {confidence:.2f})",
    }


def _classify_israel_relevance(text: str) -> tuple[str, int]:
    direct_count = sum(1 for kw in ISRAEL_KEYWORDS["direct"] if kw.lower() in text)
    indirect_count = sum(1 for kw in ISRAEL_KEYWORDS["indirect"] if kw.lower() in text)

    if direct_count >= 2:
        return "direct", min(100, 50 + direct_count * 15)
    elif direct_count == 1:
        return "direct", 60
    elif indirect_count >= 2:
        return "indirect", min(80, 30 + indirect_count * 15)
    elif indirect_count == 1:
        return "indirect", 40
    else:
        return "speculative", 10


MOTHER_ASPECTS = {
    "embryo": ("הזנה וחום בסיסיים", 80),
    "infant": ("ויסות, טיפול והתקשרות", 90),
    "child": ("עידוד למידה וחקירה", 60),
    "adult": ("תמיכה ויציבות רגשית", 40),
    "first_woman": ("הדהוד רגשי ומודל ליחסים", 50),
    "primary_woman": ("יציבות והדדיות", 60),
    "third_woman": ("ניסיון שמאפשר בחירה חדשה", 45),
    "courtship": ("פתיחות ואמון", 55),
    "marriage": ("מחויבות ושותפות", 65),
    "new_generation": ("העברה בין-דורית וטיפוח", 85),
}

FATHER_ASPECTS = {
    "embryo": ("הגנה על סביבת ההתפתחות", 85),
    "infant": ("הגנה וגבולות", 75),
    "child": ("הדרכה וסמכות מעודדת", 70),
    "adult": ("אחריות, עצמאות ואסטרטגיה", 90),
    "first_woman": ("מודל לזהות והתמודדות", 50),
    "primary_woman": ("שותפות ובניית מסגרת", 55),
    "third_woman": ("חוכמה מניסיון", 45),
    "courtship": ("יוזמה ומשא ומתן", 65),
    "marriage": ("מחויבות ואחריות הדדית", 60),
    "new_generation": ("השקעה בעתיד והורשה", 80),
}


def _mother_analogy(stage: str, event_type: str) -> dict:
    text, score = MOTHER_ASPECTS.get(stage, ("ניתוח כללי", 50))
    return {"score": score, "interpretation": f"(מטפורה אנליטית) שכבת האם: {text}"}


def _father_analogy(stage: str, event_type: str) -> dict:
    text, score = FATHER_ASPECTS.get(stage, ("ניתוח כללי", 50))
    return {"score": score, "interpretation": f"(מטפורה אנליטית) שכבת האב: {text}"}


def _son_perspective(stage: str, event_type: str, headline: str) -> dict:
    perspectives = {
        "embryo": "הסביבה מתאפיינת בתלות גבוהה ורגישות לאיומים – מבחינה התפתחותית, זוהי סביבה של בניית תשתית.",
        "infant": "הסביבה מחייבת הגנה, ויסות והזנה – מבחינה התפתחותית, זהו שלב של תלות ובניית אמון.",
        "child": "הסביבה מעודדת חקירה ולמידה – מבחינה התפתחותית, זהו שלב של רכישת יכולות.",
        "adult": "הסביבה מחייבת החלטות עצמאיות ואחריות – מבחינה התפתחותית, זהו שלב של בגרות.",
        "first_woman": "הסביבה מציגה מפגש ראשון עם קשר משמעותי – מבחינה התפתחותית, זהו שלב של גילוי עצמי דרך האחר.",
        "primary_woman": "הסביבה מתאפיינת במחויבות ויציבות – מבחינה התפתחותית, זהו שלב של בניית מערכת יחסים מרכזית.",
        "third_woman": "הסביבה מאפשרת למידה מניסיון קודם – מבחינה התפתחותית, זהו שלב של התחדשות מבוססת חוכמה.",
        "courtship": "הסביבה כוללת איתותים ומשא ומתן – מבחינה התפתחותית, זהו שלב של בניית אמון.",
        "marriage": "הסביבה מגבשת הסכם ומחויבות – מבחינה התפתחותית, זהו שלב של איחוד.",
        "new_generation": "הסביבה מכוונת לעתיד ולהעברה בין-דורית – מבחינה התפתחותית, זהו שלב של יצירת דור חדש.",
    }

    return {
        "what_is_happening": headline[:200],
        "what_can_be_perceived": perspectives.get(stage, "ניתוח כללי"),
        "developmental_meaning": f"(השערה אנליטית) האירוע משתייך לשלב '{stage}' במודל ההתפתחותי",
        "possible_long_term_pattern": "דפוס ארוך טווח ייקבע על פי הצטברות אירועים נוספים",
        "certainty": 0.5,
    }
