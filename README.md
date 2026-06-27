```markdown
# DD Engine
### Commercial Due Diligence, Automated.

**[Live Demo](https://dd-engine.streamlit.app)** · Built for Polaris Fellowship 2026
![Uploading Animation.gif…]()

---

DD Engine automates the first layer of commercial due diligence. Type a company name. In 60 seconds, get a structured investment brief — verdict, risk score, scorecard, red flags, opportunities, and a downloadable PDF formatted like a Bain deliverable.

What normally takes a junior analyst 3 days of manual research takes this tool 60 seconds.

---

## The Problem It Solves

Bain & Company's own research flags a core inefficiency in how enterprises approach investment research: analysts spend the majority of their time on data collection and synthesis before any real thinking begins. DD Engine compresses that layer from days to seconds — not to replace analyst judgment, but to free it up for what actually matters.

---

## How It Works

```

Company Name Input
        │
        ▼
   DATA PIPELINE
   ├── 15 general news articles    (NewsAPI)
   ├── 15 funding & investment articles  (NewsAPI)
   └── 10 culture & sentiment articles  (NewsAPI)
        │
        ▼
   AI SYNTHESIS
   └── LLaMA 3.3 70B (Groq)
       ├── Bain analyst persona
       ├── temperature=0 for deterministic output
       └── 5-dimension scoring framework
        │
        ▼
   REPORT GENERATION
   └── ReportLab PDF
       ├── Deal thesis + validation strip
       ├── Radar chart + score bars
       ├── Step-by-step decision process
       └── Honest data limitation disclosure
```

---

## What the Output Contains

| Section | What It Shows |
|---|---|
| Deal Thesis | One-line investment hypothesis |
| Verdict | Strong Buy / Buy / Hold / Avoid |
| Risk Score | 1–10 with reasoning |
| 5D Scorecard | Market, Financial, Management, Growth, Moat |
| Key Findings | Specific facts with numbers from real data |
| Executive Summary | 3–4 sentences with named entities |
| Market Position | Competitive landscape with named competitors |
| Financial Health | Specific funding amounts and contracts |
| Management & Culture | Sentiment from workplace signals |
| Decision Process | Exactly how the verdict was reached, step by step |
| Red Flags | Specific risks with evidence and source count |
| Opportunities | Specific upsides with market context |
| Data Limitation | Honest disclosure — confidence always marked Low |

---

## Why Confidence Is Always Marked Low

This is a deliberate design choice, not a bug.

40 public news articles is not a substitute for financial statements, management interviews, or proprietary databases. A real Bain DD engagement involves hundreds of data points across weeks of fieldwork. DD Engine is a directional signal tool — it tells you where to look, not what to decide.

Marking confidence Low and explaining exactly why is more useful — and more honest — than faking certainty. A tool that knows its limits is more trustworthy than one that doesn't.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data | NewsAPI |
| AI | LLaMA 3.3 70B via Groq |
| PDF | ReportLab |
| Charts | Matplotlib + NumPy |
| Frontend | Streamlit |
| Language | Python 3.14 |

All APIs used are free tier. No credit card required to run this locally.

---

## Run Locally

```bash
git clone https://github.com/shivamgodhwani-ship-it/dd-engine.git
cd dd-engine
pip install -r requirements.txt
```

Create `.env`:
```
NEWS_API_KEY=your_key_from_newsapi.org
GROQ_API_KEY=your_key_from_console.groq.com
```

Run:
```bash
streamlit run frontend/app.py
```

---

## Project Structure

```
dd_engine/
├── scrapers/
│   ├── news_scraper.py         general news via NewsAPI
│   ├── funding_scraper.py      funding and investment signals
│   ├── glassdoor_scraper.py    culture and sentiment signals
│   └── orchestrator.py         runs all scrapers, merges output
├── llm/
│   └── analyzer.py             Groq LLaMA with Bain analyst persona
├── reports/
│   └── generator.py            ReportLab PDF with charts
├── frontend/
│   └── app.py                  Streamlit interface
└── requirements.txt
```

---

## Known Limitations

- LLMs occasionally surface unverifiable specifics despite temperature=0 — all outputs should be verified before use
- NewsAPI free tier caps at 15 results per query — a production version would use premium data sources
- Wikipedia infobox parsing returns Unknown for companies with non-standard structures — conservative by design, no fabrication
- This is not investment advice

---

## What This Is

A 24-hour proof of capability — not a finished product.

Built to demonstrate what's possible when engineering intuition meets consulting frameworks. The goal was never to replace due diligence. It was to show that the most time-consuming part of it can be automated, transparently, with honest limitations, using only free tools.

---

*For research and demonstration purposes only. Not investment advice.*
```

**Ctrl+S** then:

```powershell
git add README.md
git commit -m "Add final README"
git push
```

Then go check your GitHub repo — it'll look sharp. 🚀
