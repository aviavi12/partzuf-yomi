import re


STAGE_WEIGHT_MATRIX = {
    "war": {
        "embryo": 0.95, "infant": 0.85, "child": 0.55, "adult": 0.90,
        "first_woman": 0.20, "primary_woman": 0.15, "third_woman": 0.25,
        "courtship": 0.10, "marriage": 0.15, "new_generation": 0.70,
    },
    "peace": {
        "embryo": 0.10, "infant": 0.15, "child": 0.30, "adult": 0.60,
        "first_woman": 0.50, "primary_woman": 0.65, "third_woman": 0.55,
        "courtship": 0.75, "marriage": 0.95, "new_generation": 0.70,
    },
    "alliance": {
        "embryo": 0.15, "infant": 0.20, "child": 0.35, "adult": 0.55,
        "first_woman": 0.60, "primary_woman": 0.85, "third_woman": 0.50,
        "courtship": 0.70, "marriage": 0.90, "new_generation": 0.45,
    },
    "economy": {
        "embryo": 0.40, "infant": 0.35, "child": 0.60, "adult": 0.90,
        "first_woman": 0.30, "primary_woman": 0.50, "third_woman": 0.45,
        "courtship": 0.35, "marriage": 0.55, "new_generation": 0.50,
    },
    "immigration": {
        "embryo": 0.85, "infant": 0.70, "child": 0.50, "adult": 0.40,
        "first_woman": 0.55, "primary_woman": 0.35, "third_woman": 0.30,
        "courtship": 0.25, "marriage": 0.20, "new_generation": 0.75,
    },
    "technology": {
        "embryo": 0.30, "infant": 0.25, "child": 0.85, "adult": 0.65,
        "first_woman": 0.35, "primary_woman": 0.40, "third_woman": 0.45,
        "courtship": 0.30, "marriage": 0.35, "new_generation": 0.90,
    },
    "family": {
        "embryo": 0.50, "infant": 0.70, "child": 0.65, "adult": 0.45,
        "first_woman": 0.55, "primary_woman": 0.75, "third_woman": 0.40,
        "courtship": 0.60, "marriage": 0.85, "new_generation": 0.95,
    },
    "elections": {
        "embryo": 0.20, "infant": 0.15, "child": 0.55, "adult": 0.95,
        "first_woman": 0.35, "primary_woman": 0.45, "third_woman": 0.40,
        "courtship": 0.65, "marriage": 0.50, "new_generation": 0.30,
    },
    "threat": {
        "embryo": 0.90, "infant": 0.80, "child": 0.50, "adult": 0.75,
        "first_woman": 0.25, "primary_woman": 0.20, "third_woman": 0.30,
        "courtship": 0.15, "marriage": 0.20, "new_generation": 0.65,
    },
    "defense": {
        "embryo": 0.85, "infant": 0.75, "child": 0.45, "adult": 0.90,
        "first_woman": 0.20, "primary_woman": 0.25, "third_woman": 0.30,
        "courtship": 0.15, "marriage": 0.20, "new_generation": 0.60,
    },
    "diplomacy": {
        "embryo": 0.15, "infant": 0.20, "child": 0.40, "adult": 0.70,
        "first_woman": 0.55, "primary_woman": 0.65, "third_woman": 0.50,
        "courtship": 0.90, "marriage": 0.75, "new_generation": 0.35,
    },
    "terrorism": {
        "embryo": 0.95, "infant": 0.85, "child": 0.45, "adult": 0.80,
        "first_woman": 0.15, "primary_woman": 0.10, "third_woman": 0.20,
        "courtship": 0.05, "marriage": 0.10, "new_generation": 0.60,
    },
    "security": {
        "embryo": 0.70, "infant": 0.60, "child": 0.40, "adult": 0.90,
        "first_woman": 0.25, "primary_woman": 0.30, "third_woman": 0.35,
        "courtship": 0.20, "marriage": 0.25, "new_generation": 0.50,
    },
    "education": {
        "embryo": 0.20, "infant": 0.35, "child": 0.95, "adult": 0.50,
        "first_woman": 0.40, "primary_woman": 0.45, "third_woman": 0.55,
        "courtship": 0.30, "marriage": 0.35, "new_generation": 0.85,
    },
    "health": {
        "embryo": 0.65, "infant": 0.90, "child": 0.60, "adult": 0.55,
        "first_woman": 0.35, "primary_woman": 0.50, "third_woman": 0.40,
        "courtship": 0.25, "marriage": 0.45, "new_generation": 0.70,
    },
    "birth": {
        "embryo": 0.70, "infant": 0.60, "child": 0.30, "adult": 0.25,
        "first_woman": 0.40, "primary_woman": 0.55, "third_woman": 0.35,
        "courtship": 0.45, "marriage": 0.65, "new_generation": 0.95,
    },
    "demography": {
        "embryo": 0.45, "infant": 0.40, "child": 0.50, "adult": 0.65,
        "first_woman": 0.35, "primary_woman": 0.50, "third_woman": 0.40,
        "courtship": 0.30, "marriage": 0.55, "new_generation": 0.90,
    },
    "energy": {
        "embryo": 0.75, "infant": 0.55, "child": 0.45, "adult": 0.85,
        "first_woman": 0.25, "primary_woman": 0.35, "third_woman": 0.30,
        "courtship": 0.20, "marriage": 0.40, "new_generation": 0.50,
    },
    "food": {
        "embryo": 0.60, "infant": 0.90, "child": 0.55, "adult": 0.50,
        "first_woman": 0.30, "primary_woman": 0.55, "third_woman": 0.35,
        "courtship": 0.20, "marriage": 0.45, "new_generation": 0.65,
    },
    "water": {
        "embryo": 0.80, "infant": 0.75, "child": 0.45, "adult": 0.55,
        "first_woman": 0.25, "primary_woman": 0.40, "third_woman": 0.30,
        "courtship": 0.15, "marriage": 0.35, "new_generation": 0.60,
    },
    "infrastructure": {
        "embryo": 0.80, "infant": 0.50, "child": 0.60, "adult": 0.75,
        "first_woman": 0.25, "primary_woman": 0.40, "third_woman": 0.35,
        "courtship": 0.20, "marriage": 0.45, "new_generation": 0.55,
    },
    "science": {
        "embryo": 0.25, "infant": 0.30, "child": 0.90, "adult": 0.60,
        "first_woman": 0.35, "primary_woman": 0.40, "third_woman": 0.50,
        "courtship": 0.25, "marriage": 0.35, "new_generation": 0.85,
    },
    "culture": {
        "embryo": 0.20, "infant": 0.30, "child": 0.80, "adult": 0.55,
        "first_woman": 0.60, "primary_woman": 0.50, "third_woman": 0.65,
        "courtship": 0.45, "marriage": 0.50, "new_generation": 0.70,
    },
    "religion": {
        "embryo": 0.35, "infant": 0.55, "child": 0.50, "adult": 0.60,
        "first_woman": 0.45, "primary_woman": 0.55, "third_woman": 0.50,
        "courtship": 0.30, "marriage": 0.65, "new_generation": 0.70,
    },
    "law": {
        "embryo": 0.25, "infant": 0.20, "child": 0.55, "adult": 0.95,
        "first_woman": 0.30, "primary_woman": 0.45, "third_woman": 0.50,
        "courtship": 0.35, "marriage": 0.55, "new_generation": 0.40,
    },
    "protest": {
        "embryo": 0.30, "infant": 0.25, "child": 0.70, "adult": 0.90,
        "first_woman": 0.40, "primary_woman": 0.35, "third_woman": 0.45,
        "courtship": 0.30, "marriage": 0.25, "new_generation": 0.55,
    },
    "leadership": {
        "embryo": 0.20, "infant": 0.15, "child": 0.45, "adult": 0.95,
        "first_woman": 0.50, "primary_woman": 0.55, "third_woman": 0.45,
        "courtship": 0.40, "marriage": 0.50, "new_generation": 0.35,
    },
    "negotiation": {
        "embryo": 0.10, "infant": 0.15, "child": 0.40, "adult": 0.65,
        "first_woman": 0.55, "primary_woman": 0.60, "third_woman": 0.50,
        "courtship": 0.95, "marriage": 0.80, "new_generation": 0.30,
    },
    "refugees": {
        "embryo": 0.75, "infant": 0.90, "child": 0.55, "adult": 0.40,
        "first_woman": 0.35, "primary_woman": 0.30, "third_woman": 0.25,
        "courtship": 0.15, "marriage": 0.20, "new_generation": 0.65,
    },
    "innovation": {
        "embryo": 0.35, "infant": 0.25, "child": 0.90, "adult": 0.60,
        "first_woman": 0.40, "primary_woman": 0.45, "third_woman": 0.50,
        "courtship": 0.35, "marriage": 0.40, "new_generation": 0.85,
    },
    "labor": {
        "embryo": 0.25, "infant": 0.20, "child": 0.55, "adult": 0.90,
        "first_woman": 0.35, "primary_woman": 0.50, "third_woman": 0.40,
        "courtship": 0.30, "marriage": 0.55, "new_generation": 0.45,
    },
    "cooperation": {
        "embryo": 0.15, "infant": 0.20, "child": 0.40, "adult": 0.55,
        "first_woman": 0.60, "primary_woman": 0.85, "third_woman": 0.50,
        "courtship": 0.75, "marriage": 0.90, "new_generation": 0.45,
    },
    "crisis": {
        "embryo": 0.90, "infant": 0.80, "child": 0.50, "adult": 0.75,
        "first_woman": 0.25, "primary_woman": 0.20, "third_woman": 0.35,
        "courtship": 0.15, "marriage": 0.20, "new_generation": 0.60,
    },
    "recovery": {
        "embryo": 0.30, "infant": 0.40, "child": 0.55, "adult": 0.65,
        "first_woman": 0.45, "primary_woman": 0.60, "third_woman": 0.80,
        "courtship": 0.50, "marriage": 0.55, "new_generation": 0.70,
    },
    "social_change": {
        "embryo": 0.25, "infant": 0.30, "child": 0.75, "adult": 0.70,
        "first_woman": 0.55, "primary_woman": 0.50, "third_woman": 0.60,
        "courtship": 0.40, "marriage": 0.45, "new_generation": 0.85,
    },
}

KEYWORD_RULES = {
    "war": {
        "keywords_en": ["war", "military", "attack", "bomb", "strike", "combat", "troops", "invasion", "battle"],
        "keywords_he": ["מלחמה", "צבא", "תקיפה", "הפצצה", "לחימה", "כוחות", "פלישה", "קרב"],
        "base_weight": 0.9,
    },
    "peace": {
        "keywords_en": ["peace", "ceasefire", "truce", "peace agreement", "reconciliation"],
        "keywords_he": ["שלום", "הפסקת אש", "הסכם שלום", "פיוס"],
        "base_weight": 0.85,
    },
    "alliance": {
        "keywords_en": ["alliance", "partnership", "cooperation", "agreement", "treaty", "pact"],
        "keywords_he": ["ברית", "שותפות", "שיתוף פעולה", "הסכם", "אמנה"],
        "base_weight": 0.8,
    },
    "economy": {
        "keywords_en": ["economy", "economic", "trade", "market", "gdp", "inflation", "recession", "growth"],
        "keywords_he": ["כלכלה", "כלכלי", "סחר", "שוק", "תל\"ג", "אינפלציה", "מיתון", "צמיחה"],
        "base_weight": 0.7,
    },
    "immigration": {
        "keywords_en": ["immigration", "migration", "immigrant", "asylum", "refugee", "aliyah"],
        "keywords_he": ["הגירה", "מהגרים", "עלייה", "פליטים", "מקלט"],
        "base_weight": 0.75,
    },
    "technology": {
        "keywords_en": ["technology", "tech", "ai", "startup", "innovation", "digital", "cyber"],
        "keywords_he": ["טכנולוגיה", "הייטק", "סטארטאפ", "חדשנות", "דיגיטלי", "סייבר"],
        "base_weight": 0.7,
    },
    "family": {
        "keywords_en": ["family", "birth", "fertility", "marriage", "children", "parenthood"],
        "keywords_he": ["משפחה", "ילודה", "פריון", "נישואין", "ילדים", "הורות"],
        "base_weight": 0.8,
    },
    "elections": {
        "keywords_en": ["election", "vote", "ballot", "campaign", "parliament", "coalition"],
        "keywords_he": ["בחירות", "הצבעה", "קלפי", "קמפיין", "כנסת", "קואליציה"],
        "base_weight": 0.75,
    },
    "threat": {
        "keywords_en": ["threat", "danger", "risk", "warning", "alert", "crisis"],
        "keywords_he": ["איום", "סכנה", "סיכון", "אזהרה", "התרעה", "משבר"],
        "base_weight": 0.85,
    },
    "defense": {
        "keywords_en": ["defense", "security", "protect", "shield", "iron dome", "intelligence"],
        "keywords_he": ["הגנה", "ביטחון", "מגן", "כיפת ברזל", "מודיעין"],
        "base_weight": 0.85,
    },
    "diplomacy": {
        "keywords_en": ["diplomacy", "diplomatic", "ambassador", "embassy", "foreign minister", "summit"],
        "keywords_he": ["דיפלומטיה", "דיפלומטי", "שגריר", "שגרירות", "שר החוץ", "פסגה"],
        "base_weight": 0.75,
    },
    "terrorism": {
        "keywords_en": ["terror", "terrorism", "terrorist", "hamas", "hezbollah", "attack"],
        "keywords_he": ["טרור", "מחבל", "חמאס", "חיזבאללה", "פיגוע"],
        "base_weight": 0.95,
    },
    "security": {
        "keywords_en": ["security", "national security", "border", "surveillance"],
        "keywords_he": ["ביטחון", "ביטחון לאומי", "גבול", "מעקב"],
        "base_weight": 0.8,
    },
    "education": {
        "keywords_en": ["education", "school", "university", "curriculum", "students", "teachers"],
        "keywords_he": ["חינוך", "בית ספר", "אוניברסיטה", "תכנית לימודים", "תלמידים", "מורים"],
        "base_weight": 0.7,
    },
    "health": {
        "keywords_en": ["health", "hospital", "medical", "vaccine", "disease", "pandemic", "who"],
        "keywords_he": ["בריאות", "בית חולים", "רפואי", "חיסון", "מחלה", "מגפה"],
        "base_weight": 0.75,
    },
    "birth": {
        "keywords_en": ["birth rate", "natality", "newborn", "fertility rate", "population growth"],
        "keywords_he": ["ילודה", "שיעור פריון", "יילוד", "גידול אוכלוסייה"],
        "base_weight": 0.85,
    },
    "demography": {
        "keywords_en": ["demography", "population", "census", "aging", "demographic"],
        "keywords_he": ["דמוגרפיה", "אוכלוסייה", "מפקד", "הזדקנות", "דמוגרפי"],
        "base_weight": 0.7,
    },
    "energy": {
        "keywords_en": ["energy", "oil", "gas", "solar", "nuclear", "renewable"],
        "keywords_he": ["אנרגיה", "נפט", "גז", "סולארי", "גרעיני", "מתחדשת"],
        "base_weight": 0.7,
    },
    "food": {
        "keywords_en": ["food", "agriculture", "famine", "hunger", "crop"],
        "keywords_he": ["מזון", "חקלאות", "רעב", "יבול"],
        "base_weight": 0.75,
    },
    "water": {
        "keywords_en": ["water", "desalination", "drought", "water supply"],
        "keywords_he": ["מים", "התפלה", "בצורת", "אספקת מים"],
        "base_weight": 0.75,
    },
    "infrastructure": {
        "keywords_en": ["infrastructure", "construction", "road", "railway", "bridge", "transport"],
        "keywords_he": ["תשתיות", "בנייה", "כביש", "רכבת", "גשר", "תחבורה"],
        "base_weight": 0.7,
    },
    "science": {
        "keywords_en": ["science", "research", "discovery", "laboratory", "experiment"],
        "keywords_he": ["מדע", "מחקר", "גילוי", "מעבדה", "ניסוי"],
        "base_weight": 0.65,
    },
    "culture": {
        "keywords_en": ["culture", "art", "music", "film", "heritage", "tradition"],
        "keywords_he": ["תרבות", "אמנות", "מוזיקה", "קולנוע", "מורשת", "מסורת"],
        "base_weight": 0.6,
    },
    "religion": {
        "keywords_en": ["religion", "religious", "faith", "prayer", "temple", "mosque", "church", "synagogue"],
        "keywords_he": ["דת", "דתי", "אמונה", "תפילה", "מקדש", "מסגד", "כנסייה", "בית כנסת"],
        "base_weight": 0.65,
    },
    "law": {
        "keywords_en": ["law", "court", "judge", "legal", "legislation", "supreme court"],
        "keywords_he": ["משפט", "בית משפט", "שופט", "חוק", "חקיקה", "בג\"ץ"],
        "base_weight": 0.7,
    },
    "protest": {
        "keywords_en": ["protest", "demonstration", "rally", "strike", "civil unrest"],
        "keywords_he": ["מחאה", "הפגנה", "עצרת", "שביתה"],
        "base_weight": 0.7,
    },
    "leadership": {
        "keywords_en": ["leader", "leadership", "president", "prime minister", "government"],
        "keywords_he": ["מנהיגות", "מנהיג", "נשיא", "ראש ממשלה", "ממשלה"],
        "base_weight": 0.75,
    },
    "negotiation": {
        "keywords_en": ["negotiation", "talks", "mediation", "dialogue", "proposal"],
        "keywords_he": ["משא ומתן", "שיחות", "תיווך", "דיאלוג", "הצעה"],
        "base_weight": 0.8,
    },
    "refugees": {
        "keywords_en": ["refugee", "displaced", "asylum seeker", "humanitarian"],
        "keywords_he": ["פליטים", "עקורים", "מבקשי מקלט", "הומניטרי"],
        "base_weight": 0.8,
    },
    "innovation": {
        "keywords_en": ["innovation", "breakthrough", "revolutionary", "pioneer"],
        "keywords_he": ["חדשנות", "פריצת דרך", "מהפכני", "חלוץ"],
        "base_weight": 0.7,
    },
    "labor": {
        "keywords_en": ["employment", "jobs", "labor", "unemployment", "workforce"],
        "keywords_he": ["תעסוקה", "משרות", "עבודה", "אבטלה", "כוח אדם"],
        "base_weight": 0.65,
    },
    "cooperation": {
        "keywords_en": ["cooperation", "joint", "bilateral", "multilateral", "collaboration"],
        "keywords_he": ["שיתוף פעולה", "משותף", "דו-צדדי", "רב-צדדי"],
        "base_weight": 0.75,
    },
    "crisis": {
        "keywords_en": ["crisis", "emergency", "collapse", "disaster", "catastrophe"],
        "keywords_he": ["משבר", "חירום", "קריסה", "אסון", "קטסטרופה"],
        "base_weight": 0.9,
    },
    "recovery": {
        "keywords_en": ["recovery", "reconstruction", "rebuilding", "rehabilitation"],
        "keywords_he": ["התאוששות", "שיקום", "בנייה מחדש", "שיקום"],
        "base_weight": 0.7,
    },
    "social_change": {
        "keywords_en": ["social change", "reform", "equality", "rights", "inclusion"],
        "keywords_he": ["שינוי חברתי", "רפורמה", "שוויון", "זכויות", "הכלה"],
        "base_weight": 0.7,
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

ISRAEL_MECHANISM_MAP = {
    "direct": {
        "label_he": "השפעה ישירה",
        "mechanism": "האירוע קשור ישירות לישראל, מתרחש בשטחה או מערב את מוסדותיה",
    },
    "indirect": {
        "label_he": "השפעה עקיפה",
        "mechanism": "האירוע משפיע על ישראל דרך שחקנים אזוריים, שותפים אסטרטגיים, או דינמיקה מזרח-תיכונית",
    },
    "speculative": {
        "label_he": "השפעה ספקולטיבית",
        "mechanism": "הקשר לישראל הוא היפותטי ומבוסס על מגמות כלליות בלבד",
    },
}

FATHER_ATTRIBUTES = {
    "protection": "הגנה",
    "force": "כוח",
    "boundary": "גבולות",
    "strategy": "אסטרטגיה",
    "action": "פעולה",
    "competition": "תחרות",
    "resources": "משאבים",
    "leadership": "מנהיגות",
    "risk": "סיכון",
    "outreach": "חיבור",
    "alliance": "ברית",
}

FATHER_EVENT_PROFILES = {
    "war":         {"protection": 0.95, "force": 0.95, "boundary": 0.90, "strategy": 0.90, "action": 0.95, "competition": 0.85, "resources": 0.80, "leadership": 0.85, "risk": 0.95, "outreach": 0.10, "alliance": 0.30},
    "peace":       {"protection": 0.30, "force": 0.10, "boundary": 0.50, "strategy": 0.70, "action": 0.40, "competition": 0.15, "resources": 0.50, "leadership": 0.65, "risk": 0.20, "outreach": 0.90, "alliance": 0.95},
    "alliance":    {"protection": 0.40, "force": 0.15, "boundary": 0.45, "strategy": 0.75, "action": 0.50, "competition": 0.30, "resources": 0.60, "leadership": 0.60, "risk": 0.25, "outreach": 0.85, "alliance": 0.95},
    "economy":     {"protection": 0.35, "force": 0.20, "boundary": 0.40, "strategy": 0.80, "action": 0.60, "competition": 0.85, "resources": 0.95, "leadership": 0.70, "risk": 0.65, "outreach": 0.55, "alliance": 0.50},
    "immigration": {"protection": 0.60, "force": 0.30, "boundary": 0.85, "strategy": 0.55, "action": 0.45, "competition": 0.40, "resources": 0.65, "leadership": 0.50, "risk": 0.50, "outreach": 0.35, "alliance": 0.25},
    "technology":  {"protection": 0.30, "force": 0.25, "boundary": 0.30, "strategy": 0.75, "action": 0.70, "competition": 0.80, "resources": 0.70, "leadership": 0.55, "risk": 0.50, "outreach": 0.60, "alliance": 0.55},
    "family":      {"protection": 0.70, "force": 0.20, "boundary": 0.55, "strategy": 0.40, "action": 0.35, "competition": 0.15, "resources": 0.50, "leadership": 0.45, "risk": 0.25, "outreach": 0.65, "alliance": 0.60},
    "elections":   {"protection": 0.30, "force": 0.35, "boundary": 0.45, "strategy": 0.90, "action": 0.80, "competition": 0.95, "resources": 0.65, "leadership": 0.95, "risk": 0.60, "outreach": 0.70, "alliance": 0.55},
    "threat":      {"protection": 0.90, "force": 0.80, "boundary": 0.85, "strategy": 0.80, "action": 0.75, "competition": 0.70, "resources": 0.55, "leadership": 0.70, "risk": 0.95, "outreach": 0.15, "alliance": 0.20},
    "defense":     {"protection": 0.95, "force": 0.85, "boundary": 0.90, "strategy": 0.85, "action": 0.80, "competition": 0.65, "resources": 0.75, "leadership": 0.80, "risk": 0.85, "outreach": 0.20, "alliance": 0.35},
    "diplomacy":   {"protection": 0.30, "force": 0.15, "boundary": 0.50, "strategy": 0.85, "action": 0.55, "competition": 0.40, "resources": 0.45, "leadership": 0.75, "risk": 0.35, "outreach": 0.90, "alliance": 0.85},
    "terrorism":   {"protection": 0.95, "force": 0.90, "boundary": 0.90, "strategy": 0.75, "action": 0.85, "competition": 0.60, "resources": 0.50, "leadership": 0.65, "risk": 0.95, "outreach": 0.05, "alliance": 0.15},
    "security":    {"protection": 0.90, "force": 0.70, "boundary": 0.85, "strategy": 0.80, "action": 0.70, "competition": 0.55, "resources": 0.65, "leadership": 0.75, "risk": 0.80, "outreach": 0.25, "alliance": 0.30},
    "education":   {"protection": 0.25, "force": 0.10, "boundary": 0.30, "strategy": 0.55, "action": 0.50, "competition": 0.40, "resources": 0.60, "leadership": 0.50, "risk": 0.20, "outreach": 0.65, "alliance": 0.45},
    "health":      {"protection": 0.75, "force": 0.15, "boundary": 0.40, "strategy": 0.55, "action": 0.50, "competition": 0.30, "resources": 0.70, "leadership": 0.50, "risk": 0.55, "outreach": 0.50, "alliance": 0.40},
    "birth":       {"protection": 0.65, "force": 0.10, "boundary": 0.35, "strategy": 0.40, "action": 0.30, "competition": 0.15, "resources": 0.55, "leadership": 0.35, "risk": 0.20, "outreach": 0.50, "alliance": 0.45},
    "demography":  {"protection": 0.40, "force": 0.15, "boundary": 0.50, "strategy": 0.65, "action": 0.40, "competition": 0.45, "resources": 0.60, "leadership": 0.50, "risk": 0.35, "outreach": 0.40, "alliance": 0.35},
    "energy":      {"protection": 0.55, "force": 0.40, "boundary": 0.50, "strategy": 0.80, "action": 0.60, "competition": 0.75, "resources": 0.95, "leadership": 0.60, "risk": 0.65, "outreach": 0.45, "alliance": 0.55},
    "food":        {"protection": 0.60, "force": 0.15, "boundary": 0.35, "strategy": 0.50, "action": 0.45, "competition": 0.35, "resources": 0.85, "leadership": 0.40, "risk": 0.45, "outreach": 0.40, "alliance": 0.35},
    "water":       {"protection": 0.70, "force": 0.20, "boundary": 0.55, "strategy": 0.60, "action": 0.50, "competition": 0.50, "resources": 0.90, "leadership": 0.50, "risk": 0.55, "outreach": 0.35, "alliance": 0.40},
    "infrastructure": {"protection": 0.50, "force": 0.30, "boundary": 0.45, "strategy": 0.70, "action": 0.75, "competition": 0.45, "resources": 0.85, "leadership": 0.55, "risk": 0.40, "outreach": 0.40, "alliance": 0.45},
    "science":     {"protection": 0.20, "force": 0.10, "boundary": 0.25, "strategy": 0.65, "action": 0.55, "competition": 0.60, "resources": 0.55, "leadership": 0.45, "risk": 0.30, "outreach": 0.65, "alliance": 0.55},
    "culture":     {"protection": 0.20, "force": 0.10, "boundary": 0.30, "strategy": 0.35, "action": 0.40, "competition": 0.25, "resources": 0.35, "leadership": 0.30, "risk": 0.15, "outreach": 0.80, "alliance": 0.60},
    "religion":    {"protection": 0.50, "force": 0.30, "boundary": 0.60, "strategy": 0.45, "action": 0.35, "competition": 0.40, "resources": 0.40, "leadership": 0.55, "risk": 0.30, "outreach": 0.55, "alliance": 0.50},
    "law":         {"protection": 0.45, "force": 0.50, "boundary": 0.90, "strategy": 0.70, "action": 0.60, "competition": 0.55, "resources": 0.45, "leadership": 0.70, "risk": 0.40, "outreach": 0.35, "alliance": 0.40},
    "protest":     {"protection": 0.35, "force": 0.60, "boundary": 0.55, "strategy": 0.50, "action": 0.85, "competition": 0.65, "resources": 0.35, "leadership": 0.55, "risk": 0.60, "outreach": 0.55, "alliance": 0.40},
    "leadership":  {"protection": 0.45, "force": 0.55, "boundary": 0.50, "strategy": 0.90, "action": 0.70, "competition": 0.75, "resources": 0.60, "leadership": 0.95, "risk": 0.55, "outreach": 0.65, "alliance": 0.60},
    "negotiation": {"protection": 0.25, "force": 0.15, "boundary": 0.55, "strategy": 0.90, "action": 0.50, "competition": 0.45, "resources": 0.40, "leadership": 0.65, "risk": 0.35, "outreach": 0.85, "alliance": 0.80},
    "refugees":    {"protection": 0.80, "force": 0.20, "boundary": 0.75, "strategy": 0.50, "action": 0.45, "competition": 0.30, "resources": 0.70, "leadership": 0.45, "risk": 0.55, "outreach": 0.40, "alliance": 0.30},
    "innovation":  {"protection": 0.20, "force": 0.15, "boundary": 0.25, "strategy": 0.70, "action": 0.75, "competition": 0.80, "resources": 0.65, "leadership": 0.55, "risk": 0.45, "outreach": 0.60, "alliance": 0.55},
    "labor":       {"protection": 0.35, "force": 0.25, "boundary": 0.40, "strategy": 0.60, "action": 0.65, "competition": 0.70, "resources": 0.80, "leadership": 0.50, "risk": 0.45, "outreach": 0.40, "alliance": 0.40},
    "cooperation": {"protection": 0.35, "force": 0.10, "boundary": 0.40, "strategy": 0.70, "action": 0.50, "competition": 0.25, "resources": 0.55, "leadership": 0.55, "risk": 0.20, "outreach": 0.90, "alliance": 0.95},
    "crisis":      {"protection": 0.85, "force": 0.70, "boundary": 0.80, "strategy": 0.75, "action": 0.80, "competition": 0.55, "resources": 0.65, "leadership": 0.75, "risk": 0.90, "outreach": 0.20, "alliance": 0.25},
    "recovery":    {"protection": 0.50, "force": 0.20, "boundary": 0.40, "strategy": 0.65, "action": 0.60, "competition": 0.30, "resources": 0.75, "leadership": 0.55, "risk": 0.30, "outreach": 0.60, "alliance": 0.55},
    "social_change": {"protection": 0.30, "force": 0.35, "boundary": 0.50, "strategy": 0.55, "action": 0.70, "competition": 0.50, "resources": 0.45, "leadership": 0.60, "risk": 0.40, "outreach": 0.70, "alliance": 0.50},
}

MOTHER_ATTRIBUTES = {
    "nutrition": "הזנה",
    "internal_protection": "הגנה פנימית",
    "containment": "הכלה",
    "stability": "יציבות",
    "care": "טיפול",
    "continuity": "המשכיות",
    "belonging": "שייכות",
    "memory": "זיכרון",
    "home": "בית",
    "regulation": "ויסות",
    "bonding": "רציפות",
}

MOTHER_EVENT_PROFILES = {
    "war":         {"nutrition": 0.15, "internal_protection": 0.90, "containment": 0.80, "stability": 0.10, "care": 0.20, "continuity": 0.15, "belonging": 0.60, "memory": 0.70, "home": 0.25, "regulation": 0.15, "bonding": 0.20},
    "peace":       {"nutrition": 0.70, "internal_protection": 0.55, "containment": 0.75, "stability": 0.90, "care": 0.80, "continuity": 0.85, "belonging": 0.80, "memory": 0.65, "home": 0.85, "regulation": 0.80, "bonding": 0.90},
    "alliance":    {"nutrition": 0.55, "internal_protection": 0.50, "containment": 0.60, "stability": 0.75, "care": 0.55, "continuity": 0.70, "belonging": 0.80, "memory": 0.50, "home": 0.60, "regulation": 0.65, "bonding": 0.75},
    "economy":     {"nutrition": 0.80, "internal_protection": 0.40, "containment": 0.50, "stability": 0.65, "care": 0.45, "continuity": 0.60, "belonging": 0.40, "memory": 0.35, "home": 0.55, "regulation": 0.70, "bonding": 0.45},
    "immigration": {"nutrition": 0.40, "internal_protection": 0.55, "containment": 0.45, "stability": 0.30, "care": 0.50, "continuity": 0.35, "belonging": 0.85, "memory": 0.75, "home": 0.90, "regulation": 0.30, "bonding": 0.40},
    "technology":  {"nutrition": 0.45, "internal_protection": 0.30, "containment": 0.35, "stability": 0.50, "care": 0.35, "continuity": 0.55, "belonging": 0.30, "memory": 0.40, "home": 0.25, "regulation": 0.40, "bonding": 0.35},
    "family":      {"nutrition": 0.90, "internal_protection": 0.80, "containment": 0.90, "stability": 0.85, "care": 0.95, "continuity": 0.90, "belonging": 0.95, "memory": 0.85, "home": 0.95, "regulation": 0.80, "bonding": 0.95},
    "elections":   {"nutrition": 0.25, "internal_protection": 0.35, "containment": 0.40, "stability": 0.45, "care": 0.30, "continuity": 0.50, "belonging": 0.65, "memory": 0.55, "home": 0.40, "regulation": 0.50, "bonding": 0.35},
    "threat":      {"nutrition": 0.15, "internal_protection": 0.85, "containment": 0.70, "stability": 0.10, "care": 0.25, "continuity": 0.20, "belonging": 0.55, "memory": 0.60, "home": 0.30, "regulation": 0.20, "bonding": 0.25},
    "defense":     {"nutrition": 0.20, "internal_protection": 0.90, "containment": 0.75, "stability": 0.30, "care": 0.30, "continuity": 0.35, "belonging": 0.60, "memory": 0.55, "home": 0.40, "regulation": 0.30, "bonding": 0.30},
    "diplomacy":   {"nutrition": 0.45, "internal_protection": 0.40, "containment": 0.55, "stability": 0.65, "care": 0.50, "continuity": 0.60, "belonging": 0.55, "memory": 0.45, "home": 0.50, "regulation": 0.60, "bonding": 0.65},
    "terrorism":   {"nutrition": 0.10, "internal_protection": 0.90, "containment": 0.75, "stability": 0.05, "care": 0.15, "continuity": 0.10, "belonging": 0.50, "memory": 0.80, "home": 0.20, "regulation": 0.10, "bonding": 0.15},
    "security":    {"nutrition": 0.25, "internal_protection": 0.85, "containment": 0.70, "stability": 0.40, "care": 0.30, "continuity": 0.40, "belonging": 0.55, "memory": 0.50, "home": 0.45, "regulation": 0.35, "bonding": 0.30},
    "education":   {"nutrition": 0.75, "internal_protection": 0.40, "containment": 0.60, "stability": 0.65, "care": 0.80, "continuity": 0.80, "belonging": 0.70, "memory": 0.75, "home": 0.55, "regulation": 0.65, "bonding": 0.70},
    "health":      {"nutrition": 0.85, "internal_protection": 0.70, "containment": 0.65, "stability": 0.55, "care": 0.90, "continuity": 0.60, "belonging": 0.50, "memory": 0.40, "home": 0.50, "regulation": 0.85, "bonding": 0.55},
    "birth":       {"nutrition": 0.90, "internal_protection": 0.75, "containment": 0.85, "stability": 0.70, "care": 0.95, "continuity": 0.95, "belonging": 0.80, "memory": 0.60, "home": 0.80, "regulation": 0.70, "bonding": 0.90},
    "demography":  {"nutrition": 0.55, "internal_protection": 0.40, "containment": 0.50, "stability": 0.55, "care": 0.50, "continuity": 0.80, "belonging": 0.70, "memory": 0.65, "home": 0.60, "regulation": 0.50, "bonding": 0.60},
    "energy":      {"nutrition": 0.70, "internal_protection": 0.40, "containment": 0.35, "stability": 0.55, "care": 0.30, "continuity": 0.50, "belonging": 0.25, "memory": 0.20, "home": 0.45, "regulation": 0.45, "bonding": 0.30},
    "food":        {"nutrition": 0.95, "internal_protection": 0.50, "containment": 0.55, "stability": 0.50, "care": 0.75, "continuity": 0.60, "belonging": 0.45, "memory": 0.40, "home": 0.65, "regulation": 0.70, "bonding": 0.50},
    "water":       {"nutrition": 0.90, "internal_protection": 0.55, "containment": 0.60, "stability": 0.50, "care": 0.60, "continuity": 0.55, "belonging": 0.35, "memory": 0.30, "home": 0.55, "regulation": 0.65, "bonding": 0.40},
    "infrastructure": {"nutrition": 0.50, "internal_protection": 0.45, "containment": 0.55, "stability": 0.70, "care": 0.40, "continuity": 0.65, "belonging": 0.45, "memory": 0.35, "home": 0.75, "regulation": 0.50, "bonding": 0.45},
    "science":     {"nutrition": 0.50, "internal_protection": 0.25, "containment": 0.35, "stability": 0.45, "care": 0.40, "continuity": 0.60, "belonging": 0.30, "memory": 0.55, "home": 0.25, "regulation": 0.40, "bonding": 0.35},
    "culture":     {"nutrition": 0.45, "internal_protection": 0.30, "containment": 0.55, "stability": 0.50, "care": 0.50, "continuity": 0.80, "belonging": 0.85, "memory": 0.90, "home": 0.70, "regulation": 0.45, "bonding": 0.65},
    "religion":    {"nutrition": 0.50, "internal_protection": 0.55, "containment": 0.65, "stability": 0.60, "care": 0.55, "continuity": 0.85, "belonging": 0.90, "memory": 0.90, "home": 0.65, "regulation": 0.55, "bonding": 0.70},
    "law":         {"nutrition": 0.30, "internal_protection": 0.50, "containment": 0.60, "stability": 0.75, "care": 0.35, "continuity": 0.65, "belonging": 0.45, "memory": 0.50, "home": 0.40, "regulation": 0.85, "bonding": 0.50},
    "protest":     {"nutrition": 0.20, "internal_protection": 0.40, "containment": 0.35, "stability": 0.20, "care": 0.30, "continuity": 0.35, "belonging": 0.70, "memory": 0.60, "home": 0.35, "regulation": 0.25, "bonding": 0.40},
    "leadership":  {"nutrition": 0.35, "internal_protection": 0.45, "containment": 0.50, "stability": 0.60, "care": 0.40, "continuity": 0.55, "belonging": 0.55, "memory": 0.50, "home": 0.45, "regulation": 0.55, "bonding": 0.45},
    "negotiation": {"nutrition": 0.40, "internal_protection": 0.40, "containment": 0.55, "stability": 0.60, "care": 0.45, "continuity": 0.55, "belonging": 0.50, "memory": 0.40, "home": 0.45, "regulation": 0.60, "bonding": 0.60},
    "refugees":    {"nutrition": 0.30, "internal_protection": 0.65, "containment": 0.50, "stability": 0.15, "care": 0.70, "continuity": 0.25, "belonging": 0.90, "memory": 0.80, "home": 0.95, "regulation": 0.20, "bonding": 0.35},
    "innovation":  {"nutrition": 0.45, "internal_protection": 0.25, "containment": 0.30, "stability": 0.45, "care": 0.35, "continuity": 0.60, "belonging": 0.30, "memory": 0.40, "home": 0.25, "regulation": 0.35, "bonding": 0.35},
    "labor":       {"nutrition": 0.65, "internal_protection": 0.35, "containment": 0.40, "stability": 0.60, "care": 0.45, "continuity": 0.55, "belonging": 0.50, "memory": 0.35, "home": 0.50, "regulation": 0.60, "bonding": 0.45},
    "cooperation": {"nutrition": 0.55, "internal_protection": 0.45, "containment": 0.60, "stability": 0.70, "care": 0.60, "continuity": 0.70, "belonging": 0.75, "memory": 0.50, "home": 0.55, "regulation": 0.65, "bonding": 0.75},
    "crisis":      {"nutrition": 0.15, "internal_protection": 0.85, "containment": 0.70, "stability": 0.10, "care": 0.25, "continuity": 0.15, "belonging": 0.55, "memory": 0.65, "home": 0.25, "regulation": 0.15, "bonding": 0.20},
    "recovery":    {"nutrition": 0.65, "internal_protection": 0.55, "containment": 0.65, "stability": 0.70, "care": 0.70, "continuity": 0.75, "belonging": 0.60, "memory": 0.60, "home": 0.70, "regulation": 0.65, "bonding": 0.65},
    "social_change": {"nutrition": 0.40, "internal_protection": 0.35, "containment": 0.40, "stability": 0.35, "care": 0.55, "continuity": 0.50, "belonging": 0.75, "memory": 0.60, "home": 0.45, "regulation": 0.40, "bonding": 0.55},
}

SON_STAGE_MODEL = {
    "embryo": {
        "can_detect": "שינויים בסביבה הבסיסית — חום, הזנה, איום ישיר על הקיום",
        "cannot_reason_about": "סיבתיות, כוונות, אסטרטגיה, יחסים בין שחקנים",
        "perception_mode": "רגישות סביבתית גולמית",
    },
    "infant": {
        "can_detect": "נוכחות/היעדרות הגנה, ויסות רגשי, תגובה לצרכים בסיסיים",
        "cannot_reason_about": "מבנים מורכבים, מדיניות, מניעים ארוכי טווח",
        "perception_mode": "תפיסה דרך תחושת ביטחון",
    },
    "child": {
        "can_detect": "דפוסים, חוקים, למידה, חקירה, שינויים בכללי המשחק",
        "cannot_reason_about": "מורכבות פוליטית עמוקה, אינטרסים סמויים, שקלול סיכונים מתקדם",
        "perception_mode": "סקרנות פעילה ולמידה",
    },
    "adult": {
        "can_detect": "דינמיקות כוח, אסטרטגיה, מדיניות, יחסי גומלין בין שחקנים",
        "cannot_reason_about": "מעט — הבוגר תופס את רוב המורכבות אך עלול להחמיץ רבדים רגשיים סמויים",
        "perception_mode": "ניתוח רציונלי ואסטרטגי",
    },
    "first_woman": {
        "can_detect": "רגשות, דינמיקות יחסים, משיכה, דחייה, מפגש עם האחר",
        "cannot_reason_about": "יציבות ארוכת טווח, מחויבות מערכתית, הורשה",
        "perception_mode": "חוויית גילוי עצמי דרך הקשר",
    },
    "primary_woman": {
        "can_detect": "יציבות, הדדיות, מחויבות, עומק הקשר, שותפות",
        "cannot_reason_about": "חידוש מתוך ניסיון כושל, בחירה מחודשת אחרי אכזבה",
        "perception_mode": "הערכה דרך עומק הקשר",
    },
    "third_woman": {
        "can_detect": "ניסיון מצטבר, חוכמה, דפוסים חוזרים, בחירה מודעת",
        "cannot_reason_about": "טוהר הרגע הראשון — ניסיון עלול להטות את התפיסה",
        "perception_mode": "חוכמה מבוססת ניסיון",
    },
    "courtship": {
        "can_detect": "איתותים, בדיקה, ניסיון קרבה, משא ומתן, בניית אמון",
        "cannot_reason_about": "תוצאות סופיות — התהליך עדיין פתוח",
        "perception_mode": "בדיקה וזהירות פעילה",
    },
    "marriage": {
        "can_detect": "מחויבות, הסכם, איחוד, שותפות מוצהרת, מבנה משותף",
        "cannot_reason_about": "מה קורה כשהמבנה מתפרק — רגרסיה לשלבים מוקדמים",
        "perception_mode": "ראיית המכלול המחויב",
    },
    "new_generation": {
        "can_detect": "העברה, הורשה, יצירה, חידוש, פוטנציאל עתידי",
        "cannot_reason_about": "עצמו כמושא — הדור החדש לא תופס את עצמו כתוצר",
        "perception_mode": "כיוון לעתיד והעברה",
    },
}

CAUSAL_CHAIN_TEMPLATES = {
    "war":         {"immediate": "הסלמה צבאית ואובדן חיים", "secondary": "שיבוש כלכלי ותזוזת אוכלוסייה", "israel_effect": "העלאת כוננות ביטחונית ולחץ דיפלומטי", "son_effect": "הסביבה הופכת מאיימת ולא צפויה"},
    "peace":       {"immediate": "הפחתת מתחים והסרת איומים", "secondary": "פתיחת ערוצי סחר ושיתוף פעולה", "israel_effect": "הזדמנות לנורמליזציה וצמצום הוצאות ביטחון", "son_effect": "הסביבה נתפסת כבטוחה ומזמינה"},
    "alliance":    {"immediate": "חיזוק הקשר הדו-צדדי", "secondary": "יצירת מסגרת אסטרטגית משותפת", "israel_effect": "הרחבת רשת הביטחון הדיפלומטית", "son_effect": "תחושת שייכות ושותפות"},
    "economy":     {"immediate": "שינוי בזרימת משאבים ותעסוקה", "secondary": "השפעה על רמת חיים ויציבות חברתית", "israel_effect": "השפעה על סחר, השקעות ותקציב ביטחון", "son_effect": "שינוי בזמינות משאבים בסיסיים"},
    "immigration": {"immediate": "תנועת אוכלוסייה ושינוי דמוגרפי", "secondary": "לחץ על משאבים ושינוי מרקם חברתי", "israel_effect": "השלכות דמוגרפיות ופוטנציאל עלייה", "son_effect": "שינוי בהרכב הסביבה המוכרת"},
    "technology":  {"immediate": "שינוי ביכולות ובנגישות", "secondary": "שיבוש שוקי עבודה ומבנים קיימים", "israel_effect": "חיזוק/איום על יתרון טכנולוגי", "son_effect": "כלים חדשים לחקירה ולמידה"},
    "family":      {"immediate": "שינוי במבנה המשפחתי", "secondary": "השלכות על דפוסי חינוך וחברות", "israel_effect": "השפעה על מדיניות רווחה ודמוגרפיה", "son_effect": "שינוי ישיר בסביבת הגדילה"},
    "elections":   {"immediate": "שינוי מנהיגות ומדיניות", "secondary": "שינוי סדרי עדיפויות ותקצוב", "israel_effect": "שינוי ביחסים דיפלומטיים וביטחוניים", "son_effect": "שינוי בכללי המשחק הסביבתיים"},
    "threat":      {"immediate": "העלאת רמת הכוננות", "secondary": "הסטת משאבים לביטחון", "israel_effect": "הגברת ערנות ומוכנות", "son_effect": "הסביבה נתפסת כמסוכנת"},
    "defense":     {"immediate": "חיזוק מערכי הגנה", "secondary": "השקעת משאבים בביטחון על חשבון תחומים אחרים", "israel_effect": "חיזוק/החלשת מעטפת ההגנה", "son_effect": "תחושת מוגנות או חשיפה"},
    "diplomacy":   {"immediate": "פתיחת ערוצי תקשורת", "secondary": "בניית מסגרת להסכמים", "israel_effect": "הרחבה/צמצום מרחב התמרון הדיפלומטי", "son_effect": "שינוי באיכות הקשרים הסביבתיים"},
    "terrorism":   {"immediate": "פגיעה ישירה באזרחים ובתשתיות", "secondary": "פגיעה בתחושת ביטחון ושגרה", "israel_effect": "הגברת פעולות ביטחון וצמצום חירויות", "son_effect": "הסביבה נתפסת כמאיימת ולא צפויה"},
    "security":    {"immediate": "חיזוק אכיפה ומעקב", "secondary": "מתח בין ביטחון לחירויות אזרח", "israel_effect": "עדכון מדיניות ביטחונית", "son_effect": "שינוי ברמת הפיקוח הנתפסת"},
    "education":   {"immediate": "שינוי בתכנים ובגישה לידע", "secondary": "השפעה על ניעות חברתית", "israel_effect": "עדכון מערכת חינוך והכשרה", "son_effect": "שינוי ישיר ביכולת למידה וחקירה"},
    "health":      {"immediate": "שינוי במצב בריאותי ובנגישות טיפול", "secondary": "לחץ על מערכות בריאות ותקציבים", "israel_effect": "התאמת מדיניות בריאות", "son_effect": "שינוי בתחושת שלמות גופנית"},
    "birth":       {"immediate": "שינוי בשיעורי ילודה", "secondary": "השלכות דמוגרפיות ארוכות טווח", "israel_effect": "השפעה על מאזן דמוגרפי", "son_effect": "שינוי בגודל הסביבה המשפחתית"},
    "demography":  {"immediate": "שינוי בהרכב אוכלוסייה", "secondary": "לחץ על שירותים ומשאבים", "israel_effect": "השלכות על מאזן דמוגרפי ותכנון", "son_effect": "שינוי בסביבה החברתית"},
    "energy":      {"immediate": "שינוי בזמינות ומחיר אנרגיה", "secondary": "השפעה על כלכלה וגיאופוליטיקה", "israel_effect": "השפעה על עצמאות אנרגטית", "son_effect": "שינוי בזמינות משאבים בסיסיים"},
    "food":        {"immediate": "שינוי בביטחון תזונתי", "secondary": "לחץ חברתי ותנודות מחירים", "israel_effect": "השפעה על יבוא מזון ויוקר מחיה", "son_effect": "שינוי ישיר בהזנה ובטיפול"},
    "water":       {"immediate": "שינוי בזמינות מים", "secondary": "מתחים אזוריים על משאבי מים", "israel_effect": "השפעה על התפלה ושיתופי פעולה אזוריים", "son_effect": "שינוי בזמינות משאב בסיסי"},
    "infrastructure": {"immediate": "שינוי ביכולת תנועה ותקשורת", "secondary": "השפעה על פיתוח אזורי וכלכלי", "israel_effect": "השפעה על פרויקטים אזוריים", "son_effect": "שינוי בסביבה הפיזית"},
    "science":     {"immediate": "גילוי או פריצת דרך", "secondary": "שינוי ביכולות ובהבנה", "israel_effect": "השפעה על מחקר ופיתוח מקומי", "son_effect": "הרחבת כלים להבנת העולם"},
    "culture":     {"immediate": "שינוי בשיח ובערכים", "secondary": "השפעה על זהות וקהילה", "israel_effect": "עדכון שיח תרבותי מקומי", "son_effect": "שינוי בנרטיב הסביבתי"},
    "religion":    {"immediate": "שינוי בפרקטיקות ובכוח מוסדות דת", "secondary": "השפעה על ערכים ונורמות", "israel_effect": "השפעה על יחסי דת-מדינה", "son_effect": "שינוי במסגרת ערכית"},
    "law":         {"immediate": "שינוי בכללים ובאכיפה", "secondary": "השפעה על זכויות וחובות", "israel_effect": "השפעה על חקיקה ובתי משפט", "son_effect": "שינוי בגבולות המותר"},
    "protest":     {"immediate": "ביטוי מחאה ציבורית", "secondary": "לחץ לשינוי מדיניות", "israel_effect": "גלי מחאה מקבילים", "son_effect": "חשיפה למתח חברתי"},
    "leadership":  {"immediate": "שינוי מנהיגות או סגנון הנהגה", "secondary": "שינוי כיוון אסטרטגי", "israel_effect": "שינוי ביחסים בין-מדינתיים", "son_effect": "שינוי בדמויות הסמכות"},
    "negotiation": {"immediate": "פתיחת ערוצי דיאלוג", "secondary": "בניית מסגרת להסכם", "israel_effect": "הרחבת/צמצום אפשרויות דיפלומטיות", "son_effect": "תהליך פתוח ולא ודאי"},
    "refugees":    {"immediate": "תנועת אוכלוסייה וסבל אנושי", "secondary": "לחץ על מדינות קולטות", "israel_effect": "לחץ הומניטרי ודיפלומטי", "son_effect": "חשיפה לפגיעות ולעקירה"},
    "innovation":  {"immediate": "יצירת פתרון חדש", "secondary": "שיבוש תבניות ישנות", "israel_effect": "חיזוק אקוסיסטם חדשנות", "son_effect": "כלים חדשים וסקרנות"},
    "labor":       {"immediate": "שינוי בשוק עבודה", "secondary": "השפעה על רמת חיים", "israel_effect": "השלכות על תעסוקה מקומית", "son_effect": "שינוי בזמינות משאבי הקיום"},
    "cooperation": {"immediate": "יצירת שותפות פעילה", "secondary": "חיזוק קשרים מערכתיים", "israel_effect": "הרחבת רשת שותפויות", "son_effect": "סביבה תומכת ומחוברת"},
    "crisis":      {"immediate": "שיבוש שגרה ומשאבים", "secondary": "לחץ על כל מערכות החברה", "israel_effect": "הערכות לתרחיש חירום", "son_effect": "הסביבה מאבדת יציבות"},
    "recovery":    {"immediate": "תחילת שיקום ובנייה מחדש", "secondary": "חזרה הדרגתית לתפקוד", "israel_effect": "לקחים ושדרוג מערכות", "son_effect": "חזרה הדרגתית ליציבות"},
    "social_change": {"immediate": "שינוי בנורמות ובציפיות", "secondary": "עדכון מוסדות ומדיניות", "israel_effect": "גלי שינוי חברתי מקבילים", "son_effect": "שינוי בכללי ההתנהגות הסביבתיים"},
}


def classify_article(headline: str, summary: str, source_name: str, language: str) -> dict:
    text = f"{headline} {summary}".lower()

    event_type, base_weight, keyword_hits = _detect_event_type(text)
    stage_scores = _compute_stage_vector(event_type)
    dominant_stage = max(stage_scores, key=stage_scores.get)
    israel_type, israel_score = _classify_israel_relevance(text)
    evidence_strength = _estimate_evidence_strength(keyword_hits, text)
    confidence = min(1.0, base_weight * 0.6 + evidence_strength * 0.2 + (0.2 if israel_score > 50 else 0))

    father = _father_analysis(event_type, dominant_stage)
    mother = _mother_analysis(event_type, dominant_stage)
    son = _son_perspective(dominant_stage, event_type, headline)
    causal = _causal_chain(event_type, israel_type)

    final_score = _calculate_final_score(
        base_weight=base_weight,
        evidence_strength=evidence_strength,
        israel_relevance=israel_score / 100.0,
        source_reliability=0.8,
        confidence=confidence,
    )

    return {
        "event_type": event_type,
        "developmental_stage": dominant_stage,
        "stage_scores": stage_scores,
        "stage_score": int(stage_scores[dominant_stage] * 100),
        "israel_relevance": israel_type,
        "israel_relevance_score": israel_score,
        "israel_mechanism": ISRAEL_MECHANISM_MAP.get(israel_type, ISRAEL_MECHANISM_MAP["speculative"]),
        "mother_analogy": mother,
        "father_analogy": father,
        "son_perspective": son,
        "causal_chain": causal,
        "scientific_context": {
            "evidence_level": "metaphorical",
            "text": "Classification based on keyword rule matching. This is an analytical framework, not a scientific claim.",
        },
        "confidence": confidence,
        "final_score": final_score,
        "reasoning_summary": f"Rule-based classification: {event_type} -> {dominant_stage} (confidence: {confidence:.2f})",
    }


def _detect_event_type(text: str) -> tuple[str, float, int]:
    scores: dict[str, float] = {}
    hit_counts: dict[str, int] = {}

    for event_type, rules in KEYWORD_RULES.items():
        keywords = rules["keywords_en"] + rules["keywords_he"]
        match_count = sum(1 for kw in keywords if kw.lower() in text)
        if match_count > 0:
            scores[event_type] = match_count * rules["base_weight"]
            hit_counts[event_type] = match_count

    if not scores:
        return "security", 0.3, 0

    best = max(scores, key=scores.get)
    return best, KEYWORD_RULES[best]["base_weight"], hit_counts[best]


def _compute_stage_vector(event_type: str) -> dict[str, float]:
    if event_type in STAGE_WEIGHT_MATRIX:
        return dict(STAGE_WEIGHT_MATRIX[event_type])
    return {s: 0.5 for s in ["embryo", "infant", "child", "adult", "first_woman",
                              "primary_woman", "third_woman", "courtship", "marriage", "new_generation"]}


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


def _estimate_evidence_strength(keyword_hits: int, text: str) -> float:
    if keyword_hits >= 5:
        return 0.9
    elif keyword_hits >= 3:
        return 0.7
    elif keyword_hits >= 1:
        return 0.5
    return 0.3


def _father_analysis(event_type: str, dominant_stage: str) -> dict:
    profile = FATHER_EVENT_PROFILES.get(event_type, {})
    if not profile:
        return {"score": 50, "interpretation": "(מטפורה אנליטית) שכבת האב: ניתוח כללי", "attributes": {}}

    avg_score = int(sum(profile.values()) / len(profile) * 100)
    top_attrs = sorted(profile.items(), key=lambda x: -x[1])[:3]
    top_labels = [f"{FATHER_ATTRIBUTES[a]}({int(s*100)})" for a, s in top_attrs]

    return {
        "score": avg_score,
        "interpretation": f"(מטפורה אנליטית) שכבת האב: {', '.join(top_labels)}",
        "attributes": {k: int(v * 100) for k, v in profile.items()},
        "dominant_attributes": [a for a, _ in top_attrs],
    }


def _mother_analysis(event_type: str, dominant_stage: str) -> dict:
    profile = MOTHER_EVENT_PROFILES.get(event_type, {})
    if not profile:
        return {"score": 50, "interpretation": "(מטפורה אנליטית) שכבת האם: ניתוח כללי", "attributes": {}}

    avg_score = int(sum(profile.values()) / len(profile) * 100)
    top_attrs = sorted(profile.items(), key=lambda x: -x[1])[:3]
    top_labels = [f"{MOTHER_ATTRIBUTES[a]}({int(s*100)})" for a, s in top_attrs]

    return {
        "score": avg_score,
        "interpretation": f"(מטפורה אנליטית) שכבת האם: {', '.join(top_labels)}",
        "attributes": {k: int(v * 100) for k, v in profile.items()},
        "dominant_attributes": [a for a, _ in top_attrs],
    }


def _son_perspective(stage: str, event_type: str, headline: str) -> dict:
    model = SON_STAGE_MODEL.get(stage, SON_STAGE_MODEL["adult"])

    return {
        "what_is_happening": headline[:200],
        "can_detect": model["can_detect"],
        "cannot_reason_about": model["cannot_reason_about"],
        "perception_mode": model["perception_mode"],
        "developmental_meaning": f"(השערה אנליטית) בשלב '{stage}' הבן תופס את האירוע דרך {model['perception_mode']}",
        "possible_long_term_pattern": "דפוס ארוך טווח ייקבע על פי הצטברות אירועים נוספים",
        "certainty": 0.5,
    }


def _causal_chain(event_type: str, israel_relevance_type: str) -> dict:
    template = CAUSAL_CHAIN_TEMPLATES.get(event_type)
    if not template:
        return {
            "event": event_type,
            "immediate_effect": "לא ניתן לקבוע ללא ניתוח ספציפי",
            "secondary_effect": "לא ניתן לקבוע ללא ניתוח ספציפי",
            "israel_effect": "לא ניתן לקבוע ללא ניתוח ספציפי",
            "son_effect": "לא ניתן לקבוע ללא ניתוח ספציפי",
            "chain_confidence": 0.3,
        }

    relevance_multiplier = {"direct": 1.0, "indirect": 0.7, "speculative": 0.4}.get(israel_relevance_type, 0.3)

    return {
        "event": event_type,
        "immediate_effect": template["immediate"],
        "secondary_effect": template["secondary"],
        "israel_effect": template["israel_effect"],
        "son_effect": template["son_effect"],
        "chain_confidence": round(0.6 * relevance_multiplier, 2),
    }


def _calculate_final_score(
    base_weight: float,
    evidence_strength: float,
    israel_relevance: float,
    source_reliability: float,
    confidence: float,
) -> int:
    temporal_fit = 0.7
    relationship_fit = 0.6

    raw = (
        base_weight
        * evidence_strength
        * (0.3 + 0.7 * israel_relevance)
        * temporal_fit
        * relationship_fit
        * source_reliability
    ) * 100

    return max(0, min(100, int(raw)))
