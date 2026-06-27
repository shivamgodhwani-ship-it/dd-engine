import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def analyze_company(company_name):
    print(f"\n🤖 AI is analyzing {company_name}...")

    with open("data/raw_data.json", "r") as f:
        raw_data = json.load(f)

    news_count = raw_data.get("news", {}).get("article_count", 0)
    fund_count = raw_data.get("funding", {}).get("total_found", 0)
    cult_count = raw_data.get("culture", {}).get("total_found", 0)
    total = news_count + fund_count + cult_count

    # Pull company facts scraped from Wikipedia
    # NOTE: cast every field to str() — company_scraper.py returns founded_year
    # as a real int (e.g. 1849), and some fields can be None. Without str(),
    # string concatenation below raises TypeError: can only concatenate str (not "int") to str
    company_facts = raw_data.get("company_facts", {})
    founded_year   = str(company_facts.get("founded_year") or "Unknown")
    headquarters   = str(company_facts.get("headquarters") or "Unknown")
    industry       = str(company_facts.get("industry") or "Unknown")
    employee_count = str(company_facts.get("employee_count") or "Unknown")
    total_raised   = str(company_facts.get("total_raised") or "Undisclosed")
    description    = str(company_facts.get("description") or "")

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    data_snippet = json.dumps(raw_data, indent=2)[:7000]
    confidence_reason = (
        f"Based on {total} public data points (news: {news_count}, "
        f"funding records: {fund_count}, employee sentiment: {cult_count}) "
        f"plus Wikipedia company profile. No financial statements, management interviews, "
        f"or proprietary data accessed. Directional signal only — not investment advice."
    )

    prompt = (
        "You are a Senior Associate at Bain & Company's Private Equity practice, "
        "three years out of Wharton. You have worked on 12 commercial due diligence projects "
        "across technology, healthcare, and consumer sectors. You write with precision — "
        "specific numbers over vague claims, so-what conclusions over raw observations, "
        "and intellectual honesty about what the data cannot tell you.\n\n"
        "Your task: produce a Commercial Due Diligence brief on " + company_name + " using only "
        "the data provided below. Do not invent facts not present in the data.\n\n"
        "COMPANY PROFILE (from Wikipedia):\n"
        "  Founded: " + founded_year + "\n"
        "  Headquarters: " + headquarters + "\n"
        "  Industry: " + industry + "\n"
        "  Employees: " + employee_count + "\n"
        "  Status: " + total_raised + "\n"
        "  Description: " + description + "\n\n"
        "THINKING FRAMEWORK — work through these mentally before writing:\n"
        "1. What is the single most important thing this data tells us about this company?\n"
        "2. What are the 3 claims that must be true for an investor to be confident here?\n"
        "3. For each claim: does the data support it (GREEN), raise doubts (YELLOW), or contradict it (RED)?\n"
        "4. What is the weakest link — the one thing that, if wrong, kills the thesis?\n"
        "5. What should an IC ask that this data cannot answer?\n\n"
        "DATA:\n" + data_snippet + "\n\n"
        "STYLE RULES:\n"
        "- Lead every field with the specific finding, not the category.\n"
        "  BAD: 'The company operates in a competitive market...'\n"
        "  GOOD: 'Pfizer holds ~7% of global pharma revenue, competing against J&J and Roche in oncology.'\n"
        "- Quantify every risk. BAD: 'Customer concentration risk.'\n"
        "  GOOD: 'Top 3 customers represent est. 40% of revenue — a single churn event is a material miss.'\n"
        "- The deal_thesis must be a single falsifiable sentence.\n\n"
        "Respond ONLY in valid JSON matching this exact schema. No preamble, no markdown, no explanation.\n\n"
        "{\n"
        '    "company": "' + company_name + '",\n'
        '    "founded_year": "' + founded_year + '",\n'
        '    "headquarters": "' + headquarters + '",\n'
        '    "total_raised": "' + total_raised + '",\n'
        '    "top_competitors": ["<competitor 1>", "<competitor 2>", "<competitor 3>"],\n'
        '    "investment_verdict": "<Strong Buy | Buy | Hold | Avoid>",\n'
        '    "verdict_reason": "<2 sentences: strongest evidence FOR verdict, then biggest risk AGAINST>",\n'
        '    "deal_thesis": "<One falsifiable sentence: [Company] is a [verdict] because [evidence], provided [condition]>",\n'
        '    "thesis_claims": [\n'
        '        {"claim": "<testable claim 1>", "status": "<GREEN|YELLOW|RED>", "evidence": "<data point>"},\n'
        '        {"claim": "<testable claim 2>", "status": "<GREEN|YELLOW|RED>", "evidence": "<data point>"},\n'
        '        {"claim": "<testable claim 3>", "status": "<GREEN|YELLOW|RED>", "evidence": "<data point>"}\n'
        '    ],\n'
        '    "executive_summary": "<3-4 sentences. Verdict first, then market context, then biggest risk, then what to verify>",\n'
        '    "market_position": "<2-3 sentences with TAM estimate, named competitors, differentiator>",\n'
        '    "tam_estimate": "<$Xbn as of [year] if inferable, else Not determinable from available sources>",\n'
        '    "financial_health": "<2-3 sentences: funding amounts, rounds, runway, red flags>",\n'
        '    "management_sentiment": "<positive | neutral | negative>",\n'
        '    "management_assessment": "<2 sentences citing Glassdoor, founder news, or leadership signals>",\n'
        '    "key_findings": [\n'
        '        "<Finding 1: specific fact first, then so-what>",\n'
        '        "<Finding 2: specific fact first, then so-what>",\n'
        '        "<Finding 3: specific fact first, then so-what>"\n'
        '    ],\n'
        '    "red_flags": [\n'
        '        "<Red flag 1: specific issue + severity>",\n'
        '        "<Red flag 2: specific issue + severity>"\n'
        '    ],\n'
        '    "opportunities": [\n'
        '        "<Opportunity 1: specific upside + condition to capture it>",\n'
        '        "<Opportunity 2: specific upside + condition to capture it>"\n'
        '    ],\n'
        '    "unanswered_questions": [\n'
        '        "<Critical IC question this data cannot answer>",\n'
        '        "<Critical IC question 2>"\n'
        '    ],\n'
        '    "scoring": {\n'
        '        "market_position": 5,\n'
        '        "financial_health": 5,\n'
        '        "management_quality": 5,\n'
        '        "growth_potential": 5,\n'
        '        "competitive_moat": 5\n'
        '    },\n'
        '    "risk_score": 5\n'
        "}"
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0
    )

    response_text = response.choices[0].message.content
    clean = response_text.strip()
    if "```" in clean:
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    analysis = json.loads(clean)

    # Force known facts from Wikipedia — never let LLM override these
    analysis["founded_year"]  = founded_year
    analysis["total_raised"]  = total_raised
    analysis["confidence_level"] = "Low"
    analysis["confidence_reason"] = confidence_reason

    os.makedirs("data", exist_ok=True)

    with open("data/analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)

    safe_name = company_name.lower().replace(" ", "_")
    with open(f"data/{safe_name}_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)

    print("✅ Analysis complete!")
    print(f"   Verdict:    {analysis.get('investment_verdict')}")
    print(f"   Risk Score: {analysis.get('risk_score')}/10")
    print(f"   Founded:    {analysis.get('founded_year')}")
    print(f"   Confidence: {analysis.get('confidence_level')}")

    return analysis


if __name__ == "__main__":
    company = input("Enter company name: ")
    analyze_company(company)