import json
import logging
import re
from datetime import datetime, timedelta

import pytz
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.news import NewsArticle, NewsSource
from app.models.analysis import EventClassification, DevelopmentalAnalysis, IsraelRelevance
from app.models.system import TelegramMessage
from app.schemas.enums import STAGE_LABELS_HE, EVENT_TYPE_LABELS_HE, DevelopmentalStage, EventType

logger = logging.getLogger(__name__)

tz = pytz.timezone(settings.timezone)

MIN_RELEVANCE_SCORE = 5

SPAM_KEYWORDS = [
    "וילות", "צימר", "השכרה", "דירות נופש", "מבצע", "הנחה", "קופון",
    "הזמן עכשיו", "החל מ-", "ש\"ח ללילה", "מחיר מיוחד", "בהנחה",
    "sale", "discount", "coupon", "booking", "rent", "hotel",
    "sponsored", "מודעה", "פרסומת", "שיתוף פעולה מסחרי",
    "קנה", "buy now", "order now", "free shipping", "משלוח חינם",
    "ביטוח", "הלוואה", "משכנתא", "קזינו", "הימורים",
    "למכירה", "להשכרה", "נדל\"ן", "דירה למכירה", "וילה להשכרה",
    "טיסות", "חבילת נופש", "מלון", "resort", "סוויטה",
    "קניון", "קולקציה", "עונת מכירות", "סייל", "בלאק פריידי",
    "הירשמו", "לפרטים חייגו", "לינק בביו", "סרטון ממומן",
    "click here", "limited offer", "act now", "בשיתוף עם",
    "ש\"ח לחודש", "ש\"ח לשנה", "שקלים",
    "שיווק", "promotion",
]

SPAM_PATTERNS = [
    r'\d+[\s]*ש["׳]ח',
    r'₪\s*\d+',
    r'החל מ[-–\s]*\d+',
    r'\d+%\s*(הנחה|off|הנחות)',
    r'\d{3,}.*ללילה',
    r'ב-?\d+.*לחודש',
]

STAGE_ICONS = {
    "embryo": "🤰", "infant": "🍼", "child": "👦", "adult": "🧑",
    "first_woman": "💃", "primary_woman": "👫", "third_woman": "🌟",
    "courtship": "💕", "marriage": "💍", "new_generation": "👶",
}

STAGE_NARRATIVE_SHORT = {
    "embryo": "עיבור",
    "infant": "יניקה",
    "child": "ילדות",
    "adult": "בגרות",
    "first_woman": "אישה ראשונה",
    "primary_woman": "אישה עיקרית",
    "third_woman": "האישה השלישית",
    "courtship": "חיזור",
    "marriage": "נישואין",
    "new_generation": "הילד המשותף",
}

STAGE_NARRATIVE_FULL = {
    "embryo": "עיבור — תשתית נבנית, הכל תלוי בסביבה. הבן עדיין לא מודע, אבל הסביבה כבר מעצבת אותו.",
    "infant": "יניקה — תלות, הגנה, ויסות בסיסי. הבן מרגיש אם מגנים עליו או לא.",
    "child": "ילדות — סקרנות, למידה, רכישת יכולות. הבן מתחיל לזהות דפוסים.",
    "adult": "בגרות — אחריות, אסטרטגיה, עצמאות. הבן מנתח ומחליט.",
    "first_woman": "אישה ראשונה — מפגש ראשון עם האחר. הבן מגלה את עצמו דרך הקשר.",
    "primary_woman": "אישה עיקרית — מחויבות ויציבות. הבן בונה מערכת יחסים מרכזית.",
    "third_woman": "האישה השלישית — חוכמה מניסיון, בחירה מודעת. הבן בוחר מתוך הבנה עמוקה.",
    "courtship": "חיזור — בדיקה, איתותים, בניית אמון. תהליך פתוח עם סיכון.",
    "marriage": "נישואין — הסכם, איחוד, שותפות. מחויבות שמגבשת מבנה.",
    "new_generation": "הילד המשותף — דור חדש, העברה, עתיד. כל מה שנבנה ביום מתגבש.",
}

FATHER_ATTR_HE = {
    "protection": "הגנה", "force": "כוח", "boundary": "גבולות",
    "strategy": "אסטרטגיה", "action": "פעולה", "competition": "תחרות",
    "resources": "משאבים", "leadership": "מנהיגות", "risk": "סיכון",
    "outreach": "חיבור", "alliance": "ברית",
}

MOTHER_ATTR_HE = {
    "nutrition": "הזנה", "internal_protection": "הגנה פנימית",
    "containment": "הכלה", "stability": "יציבות", "care": "טיפול",
    "continuity": "המשכיות", "belonging": "שייכות", "memory": "זיכרון",
    "home": "בית", "regulation": "ויסות", "bonding": "רציפות",
}

SON_PERCEPTION = {
    "embryo": "תופס שינויי סביבה בסיסיים בלבד — חום או סכנה",
    "infant": "מרגיש האם מגנים עליו, האם מזינים אותו",
    "child": "מזהה דפוסים, שואל שאלות, לומד כללים חדשים",
    "adult": "מנתח דינמיקות כוח, שוקל אסטרטגיות, לוקח אחריות",
    "first_woman": "חווה גילוי עצמי דרך הקשר הראשון",
    "primary_woman": "מעריך עומק, יציבות, הדדיות",
    "third_woman": "בוחר מתוך חוכמה — יודע מה רוצה ומה לא",
    "courtship": "בודק, מאותת, בונה אמון בזהירות",
    "marriage": "רואה את המכלול — מחויבות, שותפות, בניין משותף",
    "new_generation": "מכוון לעתיד — מה יעביר לדור הבא",
}

ALL_STAGES = [
    "embryo", "infant", "child", "adult",
    "first_woman", "primary_woman", "third_woman",
    "courtship", "marriage", "new_generation",
]

HOUR_TO_STAGE = {
    6: "embryo", 7: "embryo",
    8: "infant", 9: "infant",
    10: "child", 11: "child",
    12: "adult", 13: "adult",
    14: "first_woman", 15: "primary_woman",
    16: "third_woman",
    17: "courtship", 18: "courtship",
    19: "marriage", 20: "marriage",
    21: "new_generation", 22: "new_generation",
    23: "new_generation",
    0: "embryo", 1: "embryo", 2: "embryo",
    3: "embryo", 4: "embryo", 5: "embryo",
}


def _is_spam(headline: str) -> bool:
    h = headline.lower()
    if any(kw in h for kw in SPAM_KEYWORDS):
        return True
    for pattern in SPAM_PATTERNS:
        if re.search(pattern, headline, re.IGNORECASE):
            return True
    return False


def _classify_inline(headline: str, language: str = "he") -> dict:
    from app.classifiers.rule_classifier import classify_article
    result = classify_article(headline, "", "", language)
    stage = result.get("developmental_stage", "")
    try:
        stage_label = f" [{STAGE_LABELS_HE.get(DevelopmentalStage(stage), stage)}]"
    except ValueError:
        stage_label = f" [{stage}]"
    father = result.get("father_analogy", {})
    mother = result.get("mother_analogy", {})
    return {
        "stage": stage,
        "stage_label": stage_label,
        "father_top": father.get("dominant_attributes", [])[:2],
        "mother_top": mother.get("dominant_attributes", [])[:2],
        "father_attrs": father.get("attributes", {}),
        "mother_attrs": mother.get("attributes", {}),
    }


def _format_inline_analysis(article: dict) -> str:
    parts = []
    fa = article.get("father_top", [])
    ma = article.get("mother_top", [])
    if fa:
        parts.append(f"👨{','.join(FATHER_ATTR_HE.get(x, x) for x in fa[:2])}")
    if ma:
        parts.append(f"👩{','.join(MOTHER_ATTR_HE.get(x, x) for x in ma[:2])}")
    return " | ".join(parts) if parts else ""


def _translate_batch(texts: list[str]) -> list[str]:
    if not texts:
        return []
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source="en", target="iw")
        combined = "\n||||\n".join(texts)
        if len(combined) > 4500:
            combined = combined[:4500]
        result = translator.translate(combined)
        if result:
            parts = result.split("\n||||\n")
            if len(parts) == len(texts):
                return parts
            parts = result.split("||||")
            if len(parts) == len(texts):
                return [p.strip() for p in parts]
        return [translator.translate(t) or t for t in texts[:8]]
    except Exception:
        return texts


def _get_chat_ids() -> dict[str, str]:
    ids = {}
    if settings.telegram_chat_id_global:
        ids["global"] = settings.telegram_chat_id_global
    if settings.telegram_chat_id_israel:
        ids["israel"] = settings.telegram_chat_id_israel
    if not ids and settings.telegram_chat_id:
        ids["global"] = settings.telegram_chat_id
        ids["israel"] = settings.telegram_chat_id
    return ids


async def _send_message(bot, chat_id: str, text: str, db: AsyncSession, msg_type: str) -> dict:
    try:
        if len(text) > 4096:
            text = text[:4090] + "\n..."
        sent = await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        tg_msg = TelegramMessage(
            message_type=msg_type, content=text,
            telegram_message_id=str(sent.message_id),
            sent_at=datetime.now(tz), status="sent",
        )
        db.add(tg_msg)
        return {"status": "sent", "message_id": str(sent.message_id), "chat_id": chat_id}
    except Exception as e:
        logger.error(f"Telegram send error to {chat_id}: {e}")
        tg_msg = TelegramMessage(
            message_type=msg_type, content=text, status="failed", error=str(e),
        )
        db.add(tg_msg)
        return {"status": "error", "error": str(e), "chat_id": chat_id}


async def _load_articles(db: AsyncSession) -> list:
    hour_ago_utc = datetime.utcnow() - timedelta(hours=1)
    q = select(NewsArticle).where(
        NewsArticle.collected_at >= hour_ago_utc
    ).order_by(NewsArticle.published_at.desc())
    result = await db.execute(q)
    articles = result.scalars().all()

    if not articles:
        all_count = (await db.execute(select(func.count()).select_from(NewsArticle))).scalar() or 0
        if all_count > 0:
            q = select(NewsArticle).where(
                NewsArticle.is_analyzed == True
            ).order_by(NewsArticle.collected_at.desc()).limit(50)
            result = await db.execute(q)
            articles = result.scalars().all()

    return articles


async def _gather_analysis(db: AsyncSession, articles: list) -> dict:
    global_articles = []
    israel_articles = []
    stage_counts: dict[str, int] = {}
    all_father: dict[str, list[int]] = {}
    all_mother: dict[str, list[int]] = {}
    skipped = 0

    for article in articles:
        if _is_spam(article.headline or ""):
            skipped += 1
            continue

        source_r = await db.execute(select(NewsSource).where(NewsSource.id == article.source_id))
        source = source_r.scalar_one_or_none()
        is_israeli = source and source.source_type != "international"

        dev_r = await db.execute(select(DevelopmentalAnalysis).where(DevelopmentalAnalysis.article_id == article.id))
        dev = dev_r.scalar_one_or_none()

        if not is_israeli:
            if not dev or dev.final_score < MIN_RELEVANCE_SCORE:
                skipped += 1
                continue

        stage_label = ""
        father_top = []
        mother_top = []

        if dev and dev.developmental_stage:
            stage = dev.developmental_stage
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
            try:
                stage_label = f" [{STAGE_LABELS_HE.get(DevelopmentalStage(stage), stage)}]"
            except ValueError:
                stage_label = f" [{stage}]"

            if dev.father_attributes_json:
                try:
                    father_data = json.loads(dev.father_attributes_json)
                    for k, v in father_data.items():
                        all_father.setdefault(k, []).append(v)
                    father_top = [k for k, _ in sorted(father_data.items(), key=lambda x: -x[1])[:2]]
                except (json.JSONDecodeError, TypeError):
                    pass
            if dev.mother_attributes_json:
                try:
                    mother_data = json.loads(dev.mother_attributes_json)
                    for k, v in mother_data.items():
                        all_mother.setdefault(k, []).append(v)
                    mother_top = [k for k, _ in sorted(mother_data.items(), key=lambda x: -x[1])[:2]]
                except (json.JSONDecodeError, TypeError):
                    pass

        elif is_israeli:
            inline = _classify_inline(article.headline or "", article.language or "he")
            stage = inline["stage"]
            stage_label = inline["stage_label"]
            father_top = inline["father_top"]
            mother_top = inline["mother_top"]
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
            for k, v in inline["father_attrs"].items():
                all_father.setdefault(k, []).append(v)
            for k, v in inline["mother_attrs"].items():
                all_mother.setdefault(k, []).append(v)

        entry = {
            "headline": article.headline or "",
            "stage_label": stage_label,
            "lang": article.language,
            "father_top": father_top,
            "mother_top": mother_top,
        }
        if is_israeli:
            israel_articles.append(entry)
        else:
            global_articles.append(entry)

    en_indices = []
    en_texts = []
    for i, a in enumerate(global_articles):
        if a.get("lang") == "en" and a["headline"]:
            en_indices.append(("global", i))
            en_texts.append(a["headline"])
    for i, a in enumerate(israel_articles):
        if a.get("lang") == "en" and a["headline"]:
            en_indices.append(("israel", i))
            en_texts.append(a["headline"])

    if en_texts:
        translated = _translate_batch(en_texts)
        for idx, (src, pos) in enumerate(en_indices):
            if idx < len(translated):
                if src == "global":
                    global_articles[pos]["headline"] = translated[idx]
                else:
                    israel_articles[pos]["headline"] = translated[idx]

    dominant = max(stage_counts, key=stage_counts.get) if stage_counts else "unknown"
    try:
        dominant_he = STAGE_LABELS_HE.get(DevelopmentalStage(dominant), dominant)
    except ValueError:
        dominant_he = dominant

    avg_father = {k: int(sum(v) / len(v)) for k, v in all_father.items() if v}
    avg_mother = {k: int(sum(v) / len(v)) for k, v in all_mother.items() if v}

    logger.info(f"Filtered {skipped}, kept global={len(global_articles)} israel={len(israel_articles)}")

    return {
        "global_articles": global_articles,
        "israel_articles": israel_articles,
        "stage_counts": stage_counts,
        "dominant": dominant,
        "dominant_he": dominant_he,
        "avg_father": avg_father,
        "avg_mother": avg_mother,
        "skipped": skipped,
    }


def _top_attrs(attrs: dict, label_map: dict, n: int = 3) -> str:
    top = sorted(attrs.items(), key=lambda x: -x[1])[:n]
    return ", ".join(f"{label_map.get(k, k)}({v})" for k, v in top)


async def send_hourly_digest(db: AsyncSession) -> dict:
    if not settings.telegram_bot_token:
        return {"status": "skipped", "reason": "Telegram not configured"}

    chat_ids = _get_chat_ids()
    if not chat_ids:
        return {"status": "skipped", "reason": "No chat IDs configured"}

    articles = await _load_articles(db)
    if not articles:
        return {"status": "skipped", "reason": "No articles found"}

    data = await _gather_analysis(db, articles)

    if not data["global_articles"] and not data["israel_articles"]:
        return {"status": "skipped", "reason": f"All {data['skipped']} articles filtered as irrelevant"}

    now = datetime.now(tz)
    current_hour = now.hour
    hour_stage = HOUR_TO_STAGE.get(current_hour, "adult")

    historical = {}
    try:
        from app.services.archive_service import fetch_historical_news
        historical = await fetch_historical_news(now.date())
    except Exception as e:
        logger.warning(f"Historical fetch failed: {e}")

    msg = _format_hourly_message(now, data, hour_stage, historical)

    import telegram
    bot = telegram.Bot(token=settings.telegram_bot_token)
    fallback_id = chat_ids.get("global") or chat_ids.get("israel")
    if not fallback_id:
        return {"status": "skipped", "reason": "No chat ID"}

    result = await _send_message(bot, fallback_id, msg, db, "hourly_unified")
    await db.commit()
    return {"status": "sent", "channels": {"unified": result}}


def _format_hourly_message(now: datetime, data: dict, hour_stage: str, historical: dict | None = None) -> str:
    time_str = now.strftime("%H:%M %d/%m/%Y")
    total = len(data["global_articles"]) + len(data["israel_articles"])
    icon = STAGE_ICONS.get(hour_stage, "🧬")
    stage_name = STAGE_NARRATIVE_SHORT.get(hour_stage, hour_stage)
    dom_he = data["dominant_he"]

    lines = [
        f"📰 <b>מבזק שעתי — {time_str}</b>",
        f"{icon} <b>שעת {stage_name}</b>",
    ]

    if historical and historical.get("today_hebrew"):
        lines.append(f"📅 {historical['today_hebrew']}")
    lines.append("")

    if data["global_articles"]:
        lines.append("🌍 <b>הפרצוף היומי</b>")
        for a in data["global_articles"][:5]:
            line = f"• {a['headline'][:80]}{a['stage_label']}"
            analysis_str = _format_inline_analysis(a)
            if analysis_str:
                line += f"\n  {analysis_str}"
            lines.append(line)
        lines.append("")

    if data["israel_articles"]:
        lines.append("🇮🇱 <b>הפרצוף הזמני</b>")
        for a in data["israel_articles"][:5]:
            line = f"• {a['headline'][:80]}{a['stage_label']}"
            analysis_str = _format_inline_analysis(a)
            if analysis_str:
                line += f"\n  {analysis_str}"
            lines.append(line)
        lines.append("")

    lines.append("━━━━━━━━━━━━")
    lines.append(f"<b>פרספקטיבת הבן בשלב {stage_name}:</b>")
    lines.append(f"👁 {SON_PERCEPTION.get(hour_stage, '')}")
    lines.append("")

    if data["avg_father"]:
        lines.append(f"👨 אב: {_top_attrs(data['avg_father'], FATHER_ATTR_HE)}")
    if data["avg_mother"]:
        lines.append(f"👩 אם: {_top_attrs(data['avg_mother'], MOTHER_ATTR_HE)}")

    lines.append(f"📊 שלב דומיננטי: {dom_he} ({total})")

    if historical:
        hist_lines = _format_historical_section(historical)
        if hist_lines:
            lines.append("")
            lines.extend(hist_lines)

    lines.append("")
    lines.append("⚠️ <i>מודל אנליטי מטפורי — אין לראות בו קביעה מדעית.</i>")

    return "\n".join(lines)


def _format_historical_section(hist: dict) -> list[str]:
    lines = []
    has_any = False

    sections = [
        ("gregorian_1y", "📜", "לפני שנה (לועזי)", lambda s: s.get("label", "")),
        ("gregorian_2y", "📜", "לפני שנתיים (לועזי)", lambda s: s.get("label", "")),
        ("hebrew_1y", "🕎", "לפני שנה (עברי)",
         lambda s: f"{s.get('hebrew_label', '')} ({s.get('gregorian_label', '')})"),
        ("hebrew_2y", "🕎", "לפני שנתיים (עברי)",
         lambda s: f"{s.get('hebrew_label', '')} ({s.get('gregorian_label', '')})"),
    ]

    for key, icon, title, label_fn in sections:
        section = hist.get(key, {})
        headlines = section.get("headlines", [])
        if not headlines:
            continue
        if not has_any:
            lines.append("━━━━━━━━━━━━")
            has_any = True

        lines.append(f"{icon} <b>{title} — {label_fn(section)}</b>")
        for h in headlines[:3]:
            analysis = _classify_inline(h, "he")
            fa = [FATHER_ATTR_HE.get(x, x) for x in analysis["father_top"][:2]]
            ma = [MOTHER_ATTR_HE.get(x, x) for x in analysis["mother_top"][:2]]
            line = f"• {h[:70]}{analysis['stage_label']}"
            parts = []
            if fa:
                parts.append(f"👨{','.join(fa)}")
            if ma:
                parts.append(f"👩{','.join(ma)}")
            if parts:
                line += f"\n  {' | '.join(parts)}"
            lines.append(line)

    return lines if has_any else []


def _format_daily_full_analysis(date_str: str, data: dict, trend_text: str) -> str:
    total = len(data["global_articles"]) + len(data["israel_articles"])
    dom = data["dominant"]
    dom_he = data["dominant_he"]

    lines = [
        f"🧬 <b>סיכום יומי — {date_str}</b>",
        f"📊 סה\"כ: {total} אירועים",
        "",
    ]

    if data["global_articles"]:
        lines.append("🌍 <b>הפרצוף היומי — חדשות העולם</b>")
        for a in data["global_articles"][:5]:
            lines.append(f"• {a['headline'][:80]}{a['stage_label']}")
        lines.append("")

    if data["israel_articles"]:
        lines.append("🇮🇱 <b>הפרצוף הזמני — חדשות ישראל</b>")
        for a in data["israel_articles"][:5]:
            lines.append(f"• {a['headline'][:80]}{a['stage_label']}")
        lines.append("")

    lines.append("━━━━━━━━━━━━")
    lines.append("<b>📖 סיפור ההתפתחות של היום</b>")
    lines.append("")

    for stage in ALL_STAGES:
        count = data["stage_counts"].get(stage, 0)
        icon = STAGE_ICONS.get(stage, "•")
        full = STAGE_NARRATIVE_FULL.get(stage, stage)
        perception = SON_PERCEPTION.get(stage, "")

        if stage == dom:
            lines.append(f"<b>{icon} ▸ {full} ◂</b>")
            lines.append(f"   👁 הבן: {perception}")
            lines.append(f"   [{count} אירועים — השלב הדומיננטי]")
        elif count > 0:
            lines.append(f"{icon} {full}")
            lines.append(f"   👁 {perception} [{count}]")
        else:
            lines.append(f"{icon} <i>{STAGE_NARRATIVE_SHORT.get(stage, stage)} — שקט</i>")

    lines.append("")
    lines.append("━━━━━━━━━━━━")
    lines.append("<b>מנועי אב ואם — ממוצע יומי</b>")

    if data["avg_father"]:
        lines.append(f"👨 <b>אב:</b> {_top_attrs(data['avg_father'], FATHER_ATTR_HE, 5)}")
    if data["avg_mother"]:
        lines.append(f"👩 <b>אם:</b> {_top_attrs(data['avg_mother'], MOTHER_ATTR_HE, 5)}")

    lines.append("")

    if trend_text:
        lines.append(trend_text)
        lines.append("")

    lines.append("⚠️ <i>זהו מודל אנליטי מטפורי — אין לראות בו קביעה מדעית או רפואית.</i>")

    return "\n".join(lines)


async def send_daily_synthesis(db: AsyncSession, synthesis_text: str) -> dict:
    if not settings.telegram_bot_token:
        return {"status": "skipped", "reason": "Telegram not configured"}

    chat_ids = _get_chat_ids()
    if not chat_ids:
        return {"status": "skipped", "reason": "No chat IDs configured"}

    import telegram
    bot = telegram.Bot(token=settings.telegram_bot_token)
    fallback_id = chat_ids.get("global") or chat_ids.get("israel")
    if not fallback_id:
        return {"status": "skipped", "reason": "No chat ID"}

    result = await _send_message(bot, fallback_id, synthesis_text, db, "daily_synthesis")
    await db.commit()
    return {"status": "sent", "channels": {"unified": result}}
