import os
import json

from scrapers.news_scraper import scrape_news
from scrapers.funding_scraper import scrape_funding
from scrapers.glassdoor_scraper import scrape_glassdoor as scrape_culture
from scrapers.company_scraper import run_company_scraper


def run_all_scrapers(company_name):
    print("=" * 55)
    print(f"Running DD scrapers for: {company_name}")
    print("=" * 55)

    all_data = {}

    # --- News ---
    try:
        news_data = scrape_news(company_name)
    except Exception as e:
        print(f"[WARN] News scraper failed: {e}")
        news_data = {"article_count": 0, "articles": [], "error": str(e)}
    all_data["news"] = news_data

    # --- Funding ---
    try:
        funding_data = scrape_funding(company_name)
    except Exception as e:
        print(f"[WARN] Funding scraper failed: {e}")
        funding_data = {"total_found": 0, "error": str(e)}
    all_data["funding"] = funding_data

    # --- Culture / Glassdoor ---
    try:
        culture_data = scrape_culture(company_name)
    except Exception as e:
        print(f"[WARN] Culture scraper failed: {e}")
        culture_data = {"total_found": 0, "error": str(e)}
    all_data["culture"] = culture_data

    # --- Company facts (Wikipedia) ---
    try:
        company_facts = run_company_scraper(company_name)
    except Exception as e:
        print(f"[WARN] Company facts scraper failed: {e}")
        company_facts = {"founded_year": None, "headquarters": None, "error": str(e)}
    all_data["company_facts"] = company_facts

    # --- Save ---
    os.makedirs("data", exist_ok=True)
    with open("data/raw_data.json", "w") as f:
        json.dump(all_data, f, indent=2)

    print("=" * 55)
    print("All scrapers done! Data saved to data/raw_data.json")
    print(f"  News articles: {news_data.get('article_count', 0)}")
    print(f"  Funding articles: {funding_data.get('total_found', 0)}")
    print(f"  Culture articles: {culture_data.get('total_found', 0)}")
    print(
        f"  Company facts: founded={company_facts.get('founded_year')}, "
        f"hq={company_facts.get('headquarters')}"
    )

    failed = [
        k for k, v in all_data.items()
        if isinstance(v, dict) and "error" in v
    ]
    if failed:
        print(f"  ⚠ Sources with errors (using fallback data): {', '.join(failed)}")
    print("=" * 55)

    return all_data


if __name__ == "__main__":
    company = input("Enter company name: ").strip()
    run_all_scrapers(company)