import requests
import json
import os
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings()

load_dotenv()

def scrape_funding(company_name):
    print(f"Scraping funding data for {company_name}...")
    
    try:
        api_key = os.getenv("NEWS_API_KEY")
        
        # Search specifically for funding news
        url = f"https://newsapi.org/v2/everything"
        params = {
            "q": f"{company_name} funding OR investment OR IPO OR valuation OR raised",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 15,
            "apiKey": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        articles = []
        for item in data.get("articles", []):
            articles.append({
                "title": item["title"],
                "description": item.get("description", ""),
                "published": item["publishedAt"],
                "source": item["source"]["name"]
            })
        
        result = {
            "company": company_name,
            "funding_articles": articles,
            "total_found": len(articles)
        }
        
        os.makedirs("data", exist_ok=True)
        with open("data/funding_data.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Found {len(articles)} funding articles")
        return result
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"company": company_name, "error": str(e)}

if __name__ == "__main__":
    company = input("Enter company name: ")
    scrape_funding(company)