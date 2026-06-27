import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def scrape_news(company_name):
    print(f"Scraping news for {company_name}...")
    
    api_key = os.getenv("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/everything?q={company_name}&language=en&sortBy=publishedAt&pageSize=15&apiKey={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        articles = []
        for item in data.get("articles", []):
            articles.append({
                "title": item["title"],
                "time": item["publishedAt"],
                "source": item["source"]["name"],
                "description": item.get("description", "")
            })
        
        result = {
            "company": company_name,
            "article_count": len(articles),
            "articles": articles
        }
        
        os.makedirs("data", exist_ok=True)
        with open("data/news_data.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Found {len(articles)} articles")
        return result
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"company": company_name, "articles": [], "error": str(e)}

if __name__ == "__main__":
    company = input("Enter company name: ")
    scrape_news(company)