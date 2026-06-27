"""
DD Engine — Streamlit frontend
Styled to read like a Bain/McKinsey-style commercial due diligence brief:
ivory paper background, serif display headlines, hairline rules, restrained
brick-red accent reserved for verdict + risk signals only.
"""

import os
import sys
import streamlit as st

# Allow importing sibling packages (scrapers, llm, reports) when run via
# `streamlit run frontend/app.py` from the dd_engine root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.orchestrator import run_all_scrapers
from llm.analyzer import analyze_company
from reports.generator import generate_report


# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="DD Engine — Commercial Due Diligence",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ----------------------------------------------------------------------------
# STYLE — consulting-brief aesthetic
# ----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --paper: #FAF8F4;
  --ink: #1B2A4A;
  --ink-soft: #4A5468;
  --rule: #D8D3C7;
  --accent: #9B3A2E;
  --green: #2F6B4F;
  --yellow: #A6791F;
  --red: #9B3A2E;
}

html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background-color: var(--paper) !important;
  color: var(--ink) !important;
  font-family: 'Inter', sans-serif;
}

[data-testid="stMainBlockContainer"], .main {
  background-color: var(--paper) !important;
}

.block-container {
  max-width: 880px;
  padding-top: 2.5rem;
  padding-bottom: 4rem;
}

/* ---- Masthead ---- */
.dd-eyebrow {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-soft);
  margin-bottom: 0.5rem;
}

.dd-title {
  font-family: 'Source Serif 4', serif;
  font-weight: 700;
  font-size: 2.6rem;
  color: var(--ink);
  line-height: 1.1;
  margin: 0;
}

.dd-rule {
  border: none;
  border-top: 1px solid var(--rule);
  margin: 1.4rem 0;
}

.dd-rule-thick {
  border: none;
  border-top: 2px solid var(--ink);
  margin: 0.6rem 0 1.6rem 0;
}

/* ---- Verdict badge ---- */
.dd-verdict {
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  padding: 0.35rem 0.9rem;
  border: 1.5px solid var(--accent);
  color: var(--accent);
  border-radius: 2px;
  margin-bottom: 1rem;
}

/* ---- Thesis strip (signature element) ---- */
.dd-thesis-strip {
  display: flex;
  gap: 4px;
  margin: 1.2rem 0;
  border-radius: 2px;
  overflow: hidden;
}
.dd-thesis-seg {
  flex: 1;
  padding: 0.55rem 0.8rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: #fff;
  text-align: center;
  letter-spacing: 0.05em;
}
.dd-thesis-seg.green { background: var(--green); }
.dd-thesis-seg.yellow { background: var(--yellow); }
.dd-thesis-seg.red { background: var(--red); }

/* ---- Section heads ---- */
.dd-section-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: var(--accent);
  margin-right: 0.5rem;
}
.dd-section-head {
  font-family: 'Source Serif 4', serif;
  font-weight: 600;
  font-size: 1.3rem;
  color: var(--ink);
  border-bottom: 1px solid var(--rule);
  padding-bottom: 0.5rem;
  margin-top: 2.2rem;
  margin-bottom: 1rem;
}

/* ---- Stat strip ---- */
.dd-stat-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--ink-soft);
}
.dd-stat-value {
  font-family: 'Source Serif 4', serif;
  font-weight: 700;
  font-size: 1.6rem;
  color: var(--ink);
}

/* ---- Confidence note ---- */
.dd-confidence {
  border-left: 3px solid var(--accent);
  padding: 0.6rem 1rem;
  background: rgba(155, 58, 46, 0.05);
  font-size: 0.85rem;
  color: var(--ink-soft);
  margin: 1rem 0;
}

/* ---- Claim row ---- */
.dd-claim {
  display: flex;
  gap: 0.9rem;
  padding: 0.7rem 0;
  border-bottom: 1px solid var(--rule);
}
.dd-claim-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  padding: 0.15rem 0.5rem;
  border-radius: 2px;
  height: fit-content;
  white-space: nowrap;
  color: #fff;
}
.dd-claim-tag.green { background: var(--green); }
.dd-claim-tag.yellow { background: var(--yellow); }
.dd-claim-tag.red { background: var(--red); }

/* Hide default streamlit chrome that breaks the "printed brief" illusion */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Buttons */
.stButton button {
  font-family: 'JetBrains Mono', monospace;
  background: var(--ink);
  color: var(--paper);
  border-radius: 2px;
  border: none;
  letter-spacing: 0.05em;
  font-size: 0.8rem;
  padding: 0.6rem 1.4rem;
}
.stButton button:hover {
  background: var(--accent);
  color: #fff;
}

/* Text input */
.stTextInput input, [data-testid="stTextInput"] input {
  font-family: 'Inter', sans-serif !important;
  border: 1px solid var(--rule) !important;
  border-radius: 2px !important;
  background: #fff !important;
  color: var(--ink) !important;
}

/* Tabs */
[data-testid="stTabs"] button {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  color: var(--ink-soft) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--accent) !important;
  border-bottom-color: var(--accent) !important;
}

/* General text elements Streamlit renders */
p, span, div, label, h1, h2, h3, .stMarkdown {
  color: var(--ink);
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------
def verdict_color(verdict: str) -> str:
    v = (verdict or "").lower()
    if "strong buy" in v or v == "buy":
        return "green"
    if "hold" in v:
        return "yellow"
    return "red"


def claim_color(status: str) -> str:
    s = (status or "").upper()
    if s == "GREEN":
        return "green"
    if s == "YELLOW":
        return "yellow"
    return "red"


def render_masthead(analysis: dict):
    company = analysis.get("company", "Unknown Company")
    verdict = analysis.get("investment_verdict", "Not determined")

    st.markdown('<div class="dd-eyebrow">Commercial Due Diligence · Automated Brief</div>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="dd-title">{company}</h1>', unsafe_allow_html=True)
    st.markdown('<hr class="dd-rule-thick">', unsafe_allow_html=True)

    color = verdict_color(verdict)
    st.markdown(f'<span class="dd-verdict">{verdict.upper()}</span>', unsafe_allow_html=True)

    deal_thesis = analysis.get("deal_thesis", "")
    if deal_thesis:
        st.markdown(f"<p style='font-size:1.05rem; color:var(--ink-soft); line-height:1.6;'>{deal_thesis}</p>", unsafe_allow_html=True)

    # Signature element: thesis validation strip
    claims = analysis.get("thesis_claims", [])
    if claims:
        segs = "".join(
            f'<div class="dd-thesis-seg {claim_color(c.get("status"))}">{c.get("status", "?").upper()}</div>'
            for c in claims
        )
        st.markdown(f'<div class="dd-thesis-strip">{segs}</div>', unsafe_allow_html=True)

    # Stat row
    cols = st.columns(4)
    stats = [
        ("Overall Score", f'{analysis.get("risk_score", "—")}/10'),
        ("Founded", str(analysis.get("founded_year", "Unknown"))),
        ("Total Raised", str(analysis.get("total_raised", "Undisclosed"))),
        ("Confidence", analysis.get("confidence_level", "Low")),
    ]
    for col, (label, value) in zip(cols, stats):
        with col:
            st.markdown(f'<div class="dd-stat-label">{label}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="dd-stat-value">{value}</div>', unsafe_allow_html=True)

    conf_reason = analysis.get("confidence_reason", "")
    if conf_reason:
        st.markdown(f'<div class="dd-confidence">{conf_reason}</div>', unsafe_allow_html=True)


def section_head(num: str, title: str):
    st.markdown(
        f'<div class="dd-section-head"><span class="dd-section-num">{num}</span>{title}</div>',
        unsafe_allow_html=True,
    )


def render_body(analysis: dict):
    tabs = st.tabs(["Overview", "Market & Financials", "Scoring & Risk", "Management", "Open IC Questions"])

    with tabs[0]:
        section_head("01", "Executive Summary")
        st.write(analysis.get("executive_summary", "Not available."))

        st.markdown("**Key Findings**")
        for i, finding in enumerate(analysis.get("key_findings", []), 1):
            st.markdown(f"{i}. {finding}")

        section_head("02", "Thesis Validation")
        for claim in analysis.get("thesis_claims", []):
            tag = claim_color(claim.get("status"))
            st.markdown(
                f'<div class="dd-claim">'
                f'<span class="dd-claim-tag {tag}">{claim.get("status", "?").upper()}</span>'
                f'<div><strong>{claim.get("claim", "")}</strong><br>'
                f'<span style="color:var(--ink-soft); font-size:0.85rem;">{claim.get("evidence", "")}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with tabs[1]:
        section_head("03", "Market Position")
        st.write(analysis.get("market_position", "Not available."))

        tam = analysis.get("tam_estimate", "Not determinable from available sources")
        competitors = analysis.get("top_competitors", [])
        st.markdown(f"**Est. TAM:** {tam}")
        if competitors:
            st.markdown(f"**Named competitors:** {', '.join(competitors)}")

        section_head("04", "Financial Health")
        st.write(analysis.get("financial_health", "Not available."))

    with tabs[2]:
        section_head("05", "Scoring & Risk Profile")
        scoring = analysis.get("scoring", {})
        if scoring:
            try:
                import pandas as pd
                df = pd.DataFrame(
                    {"Dimension": [k.replace("_", " ").title() for k in scoring.keys()],
                     "Score": list(scoring.values())}
                )
                st.bar_chart(df.set_index("Dimension"))
            except ImportError:
                for k, v in scoring.items():
                    st.markdown(f"- **{k.replace('_', ' ').title()}**: {v}/10")

        st.markdown(f"**Composite risk score:** {analysis.get('risk_score', '—')}/10 (higher = more risk)")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Red Flags**")
            for flag in analysis.get("red_flags", []):
                st.markdown(f"— {flag}")
        with col2:
            st.markdown("**Opportunities**")
            for opp in analysis.get("opportunities", []):
                st.markdown(f"— {opp}")

    with tabs[3]:
        section_head("06", "Management Assessment")
        sentiment = analysis.get("management_sentiment", "neutral")
        st.markdown(f"**Overall sentiment:** {sentiment.upper()}")
        st.write(analysis.get("management_assessment", "Not available."))

    with tabs[4]:
        section_head("07", "Open Questions for IC")
        st.caption("Critical questions this analysis cannot answer from public data alone.")
        for i, q in enumerate(analysis.get("unanswered_questions", []), 1):
            st.markdown(f"**Q{i}.** {q}")


# ----------------------------------------------------------------------------
# MAIN APP
# ----------------------------------------------------------------------------
def main():
    st.markdown('<div class="dd-eyebrow">DD Engine</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="dd-title" style="font-size:1.8rem;">Commercial Due Diligence, Automated</h1>', unsafe_allow_html=True)
    st.markdown('<hr class="dd-rule">', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        company_name = st.text_input("Company name", placeholder="e.g. Pfizer", label_visibility="collapsed")
    with col2:
        run_clicked = st.button("Run Analysis", use_container_width=True)

    if run_clicked and company_name.strip():
        progress = st.empty()
        try:
            with progress.container():
                st.markdown("⏳ **Scraping news, funding, and culture data...**")
                run_all_scrapers(company_name.strip())

                st.markdown("⏳ **Analyzing with AI...**")
                analysis = analyze_company(company_name.strip())

                st.markdown("⏳ **Generating PDF report...**")
                pdf_path = generate_report(analysis)

            progress.empty()
            st.session_state["analysis"] = analysis
            st.session_state["pdf_path"] = pdf_path
            st.success(f"Analysis complete for {company_name}.")
        except FileNotFoundError:
            progress.empty()
            st.error("Could not find expected data file. Check that all scrapers ran successfully.")
        except Exception as e:
            progress.empty()
            st.error(f"Something went wrong during analysis: {e}")

    analysis = st.session_state.get("analysis")
    if analysis:
        st.markdown('<hr class="dd-rule">', unsafe_allow_html=True)
        render_masthead(analysis)

        pdf_path = st.session_state.get("pdf_path")
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "Download PDF report",
                    f,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                )

        render_body(analysis)

    st.markdown('<hr class="dd-rule">', unsafe_allow_html=True)
    st.caption("Generated by automated analysis — verify before use. Not investment advice.")


if __name__ == "__main__":
    main()