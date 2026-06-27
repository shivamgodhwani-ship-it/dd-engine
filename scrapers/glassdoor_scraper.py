import requests
import json
import os
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings()

load_dotenv()

def scrape_glassdoor(company_name):
    print(f"Scraping employee sentiment for {company_name}...")
    
    try:
        api_key = os.getenv("NEWS_API_KEY")
        
        # Search for employee culture and workplace news
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": f"{company_name} employees OR workplace OR culture OR layoffs OR hiring",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 10,
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
            "sentiment_articles": articles,
            "total_found": len(articles),
            "note": "Claude will analyze sentiment from these articles"
        }
        
        os.makedirs("data", exist_ok=True)
        with open("data/glassdoor_data.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Found {len(articles)} culture/sentiment articles")
        return result
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"company": company_name, "error": str(e)}

if __name__ == "__main__":
    company = input("Enter company name: ")
    scrape_glassdoor(company)
    