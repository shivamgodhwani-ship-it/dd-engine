"""
company_scraper.py
Pulls clean company facts from Wikipedia (no API key needed).

Uses two endpoints:
1. REST summary API -> clean description text
2. Action API (parse, prop=wikitext) -> infobox raw fields, which we then
   clean with _strip_wikitext() so we never leak {{template}} syntax.
"""

import re
import requests

USER_AGENT = "DD-Engine/1.0 (Polaris Fellowship project; contact: student-project)"
HEADERS = {"User-Agent": USER_AGENT}

SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
PARSE_URL = "https://en.wikipedia.org/w/api.php"


def _strip_wikitext(value):
    """Convert raw MediaWiki wikitext into plain readable text."""
    if value is None:
        return None
    text = str(value)

    # [[Link|Display]] or [[Link]] -> Display or Link
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)

    # {{start date|2020|01|15}} -> 2020-01-15 (best effort)
    def _start_date(m):
        parts = [p.strip() for p in m.group(1).split("|") if p.strip()]
        nums = [p for p in parts if re.match(r"^\d+$", p)]
        return "-".join(nums) if nums else ""

    text = re.sub(r"\{\{start date\|([^}]*)\}\}", _start_date, text, flags=re.I)
    text = re.sub(r"\{\{circa\|([^}]*)\}\}", lambda m: f"c. {m.group(1).split('|')[0]}", text, flags=re.I)

    # {{Unbulleted list|A|B|C}} -> A, B, C
    def _list_template(m):
        parts = [p.strip() for p in m.group(1).split("|") if p.strip()]
        return ", ".join(parts)

    text = re.sub(r"\{\{(?:Unbulleted list|Plainlist|ubl)\|([^}]*)\}\}", _list_template, text, flags=re.I)

    # {{US$|62.58billion}} or {{INR|1.2|crore}} -> US$62.58billion / INR1.2 crore
    def _currency_template(m):
        parts = [p.strip() for p in m.group(2).split("|") if p.strip()]
        return f"{m.group(1)}{' '.join(parts)}"

    text = re.sub(r"\{\{([A-Za-z$₹€£]{1,6})\|([^{}]*)\}\}", _currency_template, text)

    # Any remaining {{...}} templates -> strip entirely (don't leak raw syntax)
    text = re.sub(r"\{\{[^{}]*\}\}", "", text)

    # Reference tags <ref>...</ref> or <ref ... />
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    text = re.sub(r"<ref[^>]*/>", "", text)

    # HTML tags, bold/italic markup
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("'''", "").replace("''", "")

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text if text else None


def _get_infobox_field(wikitext, field_names):
    """Extract a field's raw value from infobox wikitext given possible field names."""
    for field in field_names:
        pattern = rf"\|\s*{re.escape(field)}\s*=\s*(.*?)\n\s*\|"
        match = re.search(pattern, wikitext, flags=re.I | re.S)
        if match:
            return match.group(1).strip()
        # Try matching to end of infobox if it's the last field before }}
        pattern_end = rf"\|\s*{re.escape(field)}\s*=\s*(.*?)\n\}}\}}"
        match = re.search(pattern_end, wikitext, flags=re.I | re.S)
        if match:
            return match.group(1).strip()
    return None


def _extract_founded_year(raw_value, description):
    """Try to pull a 4-digit year from the founded field, falling back to description."""
    candidates = []
    if raw_value:
        candidates.append(raw_value)
    if description:
        candidates.append(description)

    for c in candidates:
        match = re.search(r"\b(1[5-9]\d{2}|20[0-2]\d)\b", c)
        if match:
            return int(match.group(1))
    return None


def run_company_scraper(company_name):
    """
    Returns a dict of clean company facts pulled from Wikipedia.
    Never raises -- on any failure, returns a dict with error info
    and None/default values so callers can fail gracefully.
    """
    result = {
        "founded_year": None,
        "headquarters": None,
        "industry": None,
        "description": None,
        "total_raised": None,
        "stock_ticker": None,
        "employee_count": None,
        "source": "Wikipedia API",
    }

    title = company_name.strip().replace(" ", "_")

    # --- Step 1: Summary (clean description) ---
    try:
        resp = requests.get(SUMMARY_URL.format(title=title), headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            result["description"] = data.get("extract")
            # Use the canonical title Wikipedia resolved to, for the parse call below
            title = data.get("title", title).replace(" ", "_")
        else:
            result["description"] = None
    except requests.RequestException as e:
        result["error"] = f"summary fetch failed: {e}"
        return result

    # --- Step 2: Raw wikitext (for infobox fields) ---
    try:
        params = {
            "action": "parse",
            "page": title,
            "prop": "wikitext",
            "format": "json",
            "formatversion": "2",
        }
        resp = requests.get(PARSE_URL, headers=HEADERS, params=params, timeout=10)
        if resp.status_code != 200:
            return result

        data = resp.json()
        if "error" in data:
            result["error"] = data["error"].get("info", "unknown parse error")
            return result

        wikitext = data.get("parse", {}).get("wikitext", "")
        if not wikitext:
            return result

        # Founded
        founded_raw = _get_infobox_field(wikitext, ["founded", "foundation", "formation"])
        founded_clean = _strip_wikitext(founded_raw)
        result["founded_year"] = _extract_founded_year(founded_clean, result["description"])

        # Headquarters
        hq_city = _get_infobox_field(wikitext, ["hq_location_city", "location_city"])
        hq_full = _get_infobox_field(wikitext, ["hq_location", "headquarters", "location"])
        hq_country = _get_infobox_field(wikitext, ["hq_location_country", "location_country"])
        hq_parts = [p for p in [_strip_wikitext(hq_city), _strip_wikitext(hq_country)] if p]
        result["headquarters"] = _strip_wikitext(hq_full) or (", ".join(hq_parts) if hq_parts else None)

        # Industry
        industry_raw = _get_infobox_field(wikitext, ["industry"])
        result["industry"] = _strip_wikitext(industry_raw)

        # Stock ticker (often inside traded_as / {{NYSE|PFE}} style templates)
        traded_raw = _get_infobox_field(wikitext, ["traded_as"])
        if traded_raw:
            ticker_match = re.search(r"\{\{[^}|]+\|([A-Z]{1,6})\}\}", traded_raw)
            if ticker_match:
                result["stock_ticker"] = ticker_match.group(1)
            else:
                result["stock_ticker"] = _strip_wikitext(traded_raw)

        # Revenue (used as a proxy when total_raised isn't applicable to public co's)
        revenue_raw = _get_infobox_field(wikitext, ["revenue"])
        result["total_raised"] = _strip_wikitext(revenue_raw) or "Undisclosed"

        # Employee count
        employees_raw = _get_infobox_field(wikitext, ["num_employees", "employees"])
        result["employee_count"] = _strip_wikitext(employees_raw)

    except requests.RequestException as e:
        result["error"] = f"parse fetch failed: {e}"
    except Exception as e:
        result["error"] = f"unexpected error: {e}"

    return result


if __name__ == "__main__":
    name = input("Enter company name: ").strip()
    facts = run_company_scraper(name)
    import json
    print(json.dumps(facts, indent=2))