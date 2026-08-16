import asyncio
import logging
from datetime import date, timedelta

import feedparser
import httpx
from pyluach import dates as heb_dates

logger = logging.getLogger(__name__)

WAYBACK_CDX = "https://web.archive.org/cdx/search/cdx"
BBC_RSS_URL = "feeds.bbci.co.uk/news/world/rss.xml"


MONTHS_HE = {
    1: "ניסן", 2: "אייר", 3: "סיוון", 4: "תמוז", 5: "אב", 6: "אלול",
    7: "תשרי", 8: "חשוון", 9: "כסלו", 10: "טבת", 11: "שבט", 12: "אדר",
    13: "אדר ב׳",
}

GEMATRIA = {
    1: "א׳", 2: "ב׳", 3: "ג׳", 4: "ד׳", 5: "ה׳", 6: "ו׳", 7: "ז׳",
    8: "ח׳", 9: "ט׳", 10: "י׳", 11: "י״א", 12: "י״ב", 13: "י״ג",
    14: "י״ד", 15: "ט״ו", 16: "ט״ז", 17: "י״ז", 18: "י״ח", 19: "י״ט",
    20: "כ׳", 21: "כ״א", 22: "כ״ב", 23: "כ״ג", 24: "כ״ד", 25: "כ״ה",
    26: "כ״ו", 27: "כ״ז", 28: "כ״ח", 29: "כ״ט", 30: "ל׳",
}


def _hebrew_date_str(d: date) -> str:
    hd = heb_dates.GregorianDate(d.year, d.month, d.day).to_heb()
    day_str = GEMATRIA.get(hd.day, str(hd.day))
    month_str = MONTHS_HE.get(hd.month, str(hd.month))
    return f"{day_str} {month_str} {hd.year}"


def _hebrew_to_gregorian(heb_year: int, heb_month: int, heb_day: int) -> date | None:
    try:
        hd = heb_dates.HebrewDate(heb_year, heb_month, heb_day)
        return hd.to_pydate()
    except Exception:
        return None


def get_historical_dates(today: date) -> dict:
    hd_today = heb_dates.GregorianDate(today.year, today.month, today.day).to_heb()

    greg_1y = today.replace(year=today.year - 1)
    greg_2y = today.replace(year=today.year - 2)

    heb_1y_greg = _hebrew_to_gregorian(hd_today.year - 1, hd_today.month, hd_today.day)
    heb_2y_greg = _hebrew_to_gregorian(hd_today.year - 2, hd_today.month, hd_today.day)

    return {
        "today_hebrew": _hebrew_date_str(today),
        "gregorian_1y": {"date": greg_1y, "label": greg_1y.strftime("%d/%m/%Y")},
        "gregorian_2y": {"date": greg_2y, "label": greg_2y.strftime("%d/%m/%Y")},
        "hebrew_1y": {
            "date": heb_1y_greg,
            "label": _hebrew_date_str(heb_1y_greg) if heb_1y_greg else "?",
            "gregorian_label": heb_1y_greg.strftime("%d/%m/%Y") if heb_1y_greg else "?",
        },
        "hebrew_2y": {
            "date": heb_2y_greg,
            "label": _hebrew_date_str(heb_2y_greg) if heb_2y_greg else "?",
            "gregorian_label": heb_2y_greg.strftime("%d/%m/%Y") if heb_2y_greg else "?",
        },
    }


def translate_batch(texts: list[str]) -> list[str]:
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
        return [translator.translate(t) or t for t in texts[:5]]
    except Exception as e:
        logger.warning(f"Batch translation failed: {e}")
        return texts


async def _fetch_wayback_headlines(target_date: date, max_headlines: int = 4) -> list[str]:
    ts = target_date.strftime("%Y%m%d")
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            from_date = (target_date - timedelta(days=7)).strftime("%Y%m%d")
            to_date = (target_date + timedelta(days=7)).strftime("%Y%m%d") + "235959"

            cdx_resp = await client.get(WAYBACK_CDX, params={
                "url": f"http://{BBC_RSS_URL}",
                "from": from_date,
                "to": to_date,
                "output": "json",
                "limit": "5",
                "fl": "timestamp",
            })

            if cdx_resp.status_code != 200:
                return []

            rows = cdx_resp.json()
            if len(rows) < 2:
                return []

            target_int = int(ts + "120000")
            timestamps = [row[0] for row in rows[1:]]
            best_ts = min(timestamps, key=lambda t: abs(int(t) - target_int))

            raw_url = f"https://web.archive.org/web/{best_ts}id_/http://{BBC_RSS_URL}"

            rss_resp = await client.get(raw_url, timeout=10.0, follow_redirects=True)
            feed = feedparser.parse(rss_resp.text)

            headlines = []
            for entry in feed.entries[:max_headlines]:
                title = entry.get("title", "").strip()
                if title:
                    headlines.append(title)

            return headlines

    except Exception as e:
        logger.warning(f"Wayback fetch failed for {target_date}: {e}")
        return []


async def fetch_historical_news(today: date) -> dict:
    hist = get_historical_dates(today)

    dates_to_fetch = [
        ("gregorian_1y", hist["gregorian_1y"]["date"]),
        ("gregorian_2y", hist["gregorian_2y"]["date"]),
    ]

    heb_1y_date = hist["hebrew_1y"]["date"]
    heb_2y_date = hist["hebrew_2y"]["date"]
    if heb_1y_date:
        dates_to_fetch.append(("hebrew_1y", heb_1y_date))
    if heb_2y_date:
        dates_to_fetch.append(("hebrew_2y", heb_2y_date))

    tasks = [_fetch_wayback_headlines(d) for _, d in dates_to_fetch]
    fetched = await asyncio.gather(*tasks, return_exceptions=True)

    raw_headlines: dict[str, list[str]] = {}
    all_en_headlines = []
    for i, (key, _) in enumerate(dates_to_fetch):
        result = fetched[i]
        if isinstance(result, Exception):
            raw_headlines[key] = []
        else:
            raw_headlines[key] = result
            all_en_headlines.extend(result)

    translated = translate_batch(all_en_headlines) if all_en_headlines else []

    idx = 0
    translated_map: dict[str, list[str]] = {}
    for key, _ in dates_to_fetch:
        count = len(raw_headlines.get(key, []))
        translated_map[key] = translated[idx:idx + count]
        idx += count

    results = {
        "today_hebrew": hist["today_hebrew"],
        "gregorian_1y": {
            "label": hist["gregorian_1y"]["label"],
            "headlines": translated_map.get("gregorian_1y", []),
        },
        "gregorian_2y": {
            "label": hist["gregorian_2y"]["label"],
            "headlines": translated_map.get("gregorian_2y", []),
        },
        "hebrew_1y": {
            "hebrew_label": hist["hebrew_1y"]["label"],
            "gregorian_label": hist["hebrew_1y"]["gregorian_label"],
            "headlines": translated_map.get("hebrew_1y", []),
        },
        "hebrew_2y": {
            "hebrew_label": hist["hebrew_2y"]["label"],
            "gregorian_label": hist["hebrew_2y"]["gregorian_label"],
            "headlines": translated_map.get("hebrew_2y", []),
        },
    }

    return results
