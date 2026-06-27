from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak, KeepTogether)
from reportlab.platypus import Image as RLImage
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase.pdfmetrics import stringWidth
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json, os
from datetime import datetime
from functools import partial

# ------------------------------------------------------------------
# PALETTE
# ------------------------------------------------------------------
INK    = colors.HexColor("#1A1A2E")
NAVY   = colors.HexColor("#16213E")
MUTED  = colors.HexColor("#6B7280")
RULE   = colors.HexColor("#D8DCE3")
ACCENT = colors.HexColor("#8C1D2B")   # oxblood
GOOD   = colors.HexColor("#2F6F4F")   # green
AMBER  = colors.HexColor("#B45309")   # yellow/amber
PAPER  = colors.white

W, H = A4
CW   = W - 36 * mm   # content width (18mm margins)

TRAFFIC = {
    "GREEN":  ("#2F6F4F", "#F0FAF4"),
    "YELLOW": ("#B45309", "#FFFBEB"),
    "RED":    ("#8C1D2B", "#FEF2F2"),
}

# ------------------------------------------------------------------
# STYLES
# ------------------------------------------------------------------
def S(name, **kw):
    base = dict(fontName='Helvetica', fontSize=9.5, textColor=INK, leading=14)
    presets = {
        'kicker':       dict(fontSize=8, textColor=MUTED, fontName='Helvetica-Bold'),
        'company':      dict(fontSize=30, textColor=NAVY, fontName='Helvetica-Bold', leading=34),
        'sub':          dict(fontSize=9.5, textColor=MUTED, leading=13),
        'verdictbadge': dict(fontSize=9.5, textColor=ACCENT, fontName='Helvetica-Bold'),
        'mvalue':       dict(fontSize=16, textColor=NAVY, fontName='Helvetica-Bold'),
        'mlabel':       dict(fontSize=7, textColor=MUTED),
        'notetext':     dict(fontSize=8.5, textColor=INK, leading=13),
        'sectionnum':   dict(fontSize=9, textColor=ACCENT, fontName='Helvetica-Bold'),
        'h2':           dict(fontSize=12.5, textColor=NAVY, fontName='Helvetica-Bold'),
        'h3':           dict(fontSize=10, textColor=NAVY, fontName='Helvetica-Bold', spaceAfter=4),
        'thesis':       dict(fontSize=10.5, textColor=INK, leading=17),
        'find':         dict(fontSize=9.5, textColor=INK, leading=15, leftIndent=2),
        'flagtext':     dict(fontSize=9.5, textColor=INK, leading=14),
        'body':         dict(fontSize=9.5, textColor=INK, leading=15),
        'small':        dict(fontSize=7.5, textColor=MUTED, fontName='Helvetica-Oblique'),
        'claimtext':    dict(fontSize=9, textColor=INK, leading=13),
        'claimlabel':   dict(fontSize=7.5, fontName='Helvetica-Bold'),
        'unanswered':   dict(fontSize=9, textColor=INK, leading=14, leftIndent=2),
    }
    cfg = {**base, **presets.get(name, {}), **kw}
    return ParagraphStyle(name + str(id(kw)), **cfg)


def safe(text):
    return str(text).encode('cp1252', 'replace').decode('cp1252')


SCORE_KEYS   = ['market_position', 'financial_health', 'management_quality',
                 'growth_potential', 'competitive_moat']
SCORE_LABELS = {
    'market_position':   'Market Position',
    'financial_health':  'Financial Health',
    'management_quality':'Management',
    'growth_potential':  'Growth Potential',
    'competitive_moat':  'Competitive Moat',
}


def normalized_scoring(data):
    raw = data.get("scoring", {})
    return {k: raw.get(k, 5) for k in SCORE_KEYS}


def overall_score(data):
    if "overall_score" in data:
        return data["overall_score"]
    scoring = normalized_scoring(data)
    return round(sum(scoring.values()) / len(scoring), 1)


def sentiment_color(sentiment):
    s = (sentiment or "").lower()
    if s == "positive": return "#2F6F4F"
    if s == "negative": return "#8C1D2B"
    return "#6B7280"


# ------------------------------------------------------------------
# CHARTS
# ------------------------------------------------------------------
def radar_chart(scoring, path="data/radar.png"):
    cats = ['Market\nPosition', 'Financial\nHealth', 'Management',
            'Growth\nPotential', 'Competitive\nMoat']
    keys = ['market_position', 'financial_health', 'management_quality',
            'growth_potential', 'competitive_moat']
    vals   = [scoring.get(k, 5) for k in keys]
    angles = np.linspace(0, 2 * np.pi, len(cats), endpoint=False).tolist()
    v2, a2 = vals + [vals[0]], angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(3.4, 3.4), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.plot(a2, v2, '-', lw=1.6, color='#16213E')
    ax.fill(a2, v2, alpha=0.10, color='#16213E')
    ax.plot(a2, v2, 'o', ms=3.5, color='#16213E')
    ax.set_xticks(angles)
    ax.set_xticklabels(cats, color='#1A1A2E', size=7)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2','4','6','8','10'], color='#9CA3AF', size=6)
    ax.grid(color='#E5E7EB', lw=0.6)
    ax.spines['polar'].set_color('#E5E7EB')
    plt.tight_layout(pad=1.2)
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


def score_bars(scoring, path="data/scores.png"):
    labels = ['Market Position', 'Financial Health', 'Management',
              'Growth Potential', 'Competitive Moat']
    keys   = ['market_position', 'financial_health', 'management_quality',
               'growth_potential', 'competitive_moat']
    vals   = [scoring.get(k, 5) for k in keys]
    weakest = min(vals)
    bar_colors = ['#8C1D2B' if v == weakest else '#16213E' for v in vals]

    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    bars = ax.barh(labels, vals, color=bar_colors, height=0.5)
    ax.invert_yaxis()
    for bar, val in zip(bars, vals):
        ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height() / 2,
                f'{val}/10', va='center', color='#1A1A2E', size=7.5)
    ax.set_xlim(0, 11.5)
    ax.set_xticks([0, 2, 4, 6, 8, 10])
    ax.tick_params(colors='#9CA3AF', labelsize=7)
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#E5E7EB')
    plt.setp(ax.get_yticklabels(), color='#1A1A2E', size=7.5)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


# ------------------------------------------------------------------
# CHROME (running header/footer)
# ------------------------------------------------------------------
def _chrome(canvas, doc, company_label):
    canvas.saveState()
    page_num = canvas.getPageNumber()
    if page_num > 1:
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.6)
        canvas.line(18*mm, H - 16*mm, W - 18*mm, H - 16*mm)
        canvas.setFont('Helvetica-Bold', 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(18*mm, H - 13.5*mm, company_label)
        canvas.drawRightString(W - 18*mm, H - 13.5*mm,
                               "DUE DILIGENCE BRIEF — CONFIDENTIAL")
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(18*mm, 10*mm, "Generated by automated analysis — verify before use")
    canvas.drawRightString(W - 18*mm, 10*mm, str(page_num))
    canvas.restoreState()


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------
def metrics_strip(data):
    overall   = overall_score(data)
    founded   = safe(data.get("founded_year", "Unknown"))
    raised    = safe(data.get("total_raised", "Undisclosed"))
    confidence = safe(data.get("confidence_level", data.get("confidence", "Low")))

    cells      = [(f"{overall}/10", "OVERALL SCORE"), (founded, "FOUNDED"),
                  (raised, "TOTAL RAISED"), (confidence, "CONFIDENCE")]
    vals_row   = [Paragraph(safe(v), S('mvalue')) for v, _ in cells]
    labels_row = [Paragraph(l, S('mlabel')) for _, l in cells]

    t = Table([vals_row, labels_row], colWidths=[CW / 4] * 4)
    t.setStyle(TableStyle([
        ('LINEABOVE',  (0, 0), (-1, 0), 0.75, RULE),
        ('LINEBELOW',  (0, 1), (-1, 1), 0.75, RULE),
        ('LINEAFTER',  (0, 0), (-2, -1), 0.5, RULE),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
    ]))
    return t


def confidence_note(data):
    conf   = safe(data.get("confidence_level", data.get("confidence", "Low")))
    reason = safe(data.get("confidence_reason",
        "Limited public data sources were available; treat conclusions as directional."))
    text   = f'<font color="#8C1D2B"><b>LOW CONFIDENCE</b></font> — {reason}'
    box    = Table([[Paragraph(text, S('notetext'))]], colWidths=[CW])
    box.setStyle(TableStyle([
        ('LINEBEFORE',    (0, 0), (0, -1), 2, ACCENT),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return [Spacer(1, 8), box]


def section_header(number, title):
    row  = Table([[Paragraph(number, S('sectionnum')), Paragraph(title, S('h2'))]],
                 colWidths=[10*mm, CW - 10*mm])
    row.setStyle(TableStyle([
        ('VALIGN',        (0,0), (-1,-1), 'BOTTOM'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 0),
    ]))
    rule = HRFlowable(width=CW, thickness=1, color=NAVY,
                      spaceBefore=0, spaceAfter=12)
    return [row, rule]


# ------------------------------------------------------------------
# SECTION 1: COVER PAGE
# ------------------------------------------------------------------
def cover_page(data, company):
    verdict = safe(data.get("investment_verdict",
                             data.get("verdict", "Analysis Complete"))).upper()
    today   = datetime.now().strftime("%B %d, %Y")

    flow = [Spacer(1, 22*mm)]
    flow.append(Paragraph("CONFIDENTIAL&nbsp;&nbsp;·&nbsp;&nbsp;AUTOMATED ANALYSIS", S('kicker')))
    flow.append(Spacer(1, 6))
    flow.append(Paragraph(safe(company), S('company')))
    flow.append(HRFlowable(width=40*mm, thickness=2, color=ACCENT,
                            spaceBefore=10, spaceAfter=10, hAlign='LEFT'))
    flow.append(Paragraph(
        f"Commercial Due Diligence Brief&nbsp;&nbsp;·&nbsp;&nbsp;Prepared {today}", S('sub')))
    flow.append(Spacer(1, 16*mm))

    # Verdict badge
    badge_w = stringWidth(verdict, 'Helvetica-Bold', 9.5) + 28
    badge   = Table([[Paragraph(verdict, S('verdictbadge'))]], colWidths=[badge_w])
    badge.hAlign = 'LEFT'
    badge.setStyle(TableStyle([
        ('BOX',           (0,0), (-1,-1), 0.75, ACCENT),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 14),
        ('RIGHTPADDING',  (0,0), (-1,-1), 14),
    ]))
    flow.append(badge)

    verdict_reason = data.get("verdict_reason")
    if verdict_reason:
        flow.append(Spacer(1, 8))
        flow.append(Paragraph(safe(verdict_reason), S('sub')))

    flow.append(Spacer(1, 14*mm))
    flow.append(metrics_strip(data))
    flow += confidence_note(data)

    sources = safe(data.get("sources",
        "News coverage, funding records, employee sentiment, public filings"))
    flow.append(Spacer(1, 55*mm))
    flow.append(HRFlowable(width=CW, thickness=0.5, color=RULE,
                            spaceBefore=0, spaceAfter=8))
    flow.append(Paragraph(
        f"DATA SOURCES&nbsp;&nbsp;·&nbsp;&nbsp;{sources}", S('mlabel')))
    flow.append(PageBreak())
    return flow


# ------------------------------------------------------------------
# SECTION 2: VERDICT & THESIS (verdict-first, Bain style)
# ------------------------------------------------------------------
def verdict_thesis_section(data):
    flow = section_header("01", "INVESTMENT VERDICT & DEAL THESIS")

    # Deal thesis in accent box
    thesis = safe(data.get("deal_thesis", "No deal thesis generated."))
    thesis_box = Table([[Paragraph(thesis, S('thesis'))]], colWidths=[CW])
    thesis_box.setStyle(TableStyle([
        ('LINEBEFORE',    (0,0), (0,-1), 3, ACCENT),
        ('LEFTPADDING',   (0,0), (-1,-1), 12),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor("#FDF8F8")),
    ]))
    flow += [thesis_box, Spacer(1, 14)]

    # Thesis claims with traffic lights
    claims = data.get("thesis_claims", [])
    if claims:
        flow.append(Paragraph("Thesis Validation", S('h3')))
        flow.append(Spacer(1, 4))

        for claim in claims:
            status   = str(claim.get("status", "YELLOW")).upper()
            ink_hex, bg_hex = TRAFFIC.get(status, TRAFFIC["YELLOW"])
            ink_color = colors.HexColor(ink_hex)
            bg_color  = colors.HexColor(bg_hex)

            label_cell = Table(
                [[Paragraph(status, S('claimlabel', textColor=ink_color))]],
                colWidths=[18*mm]
            )
            label_cell.setStyle(TableStyle([
                ('BACKGROUND',    (0,0), (-1,-1), bg_color),
                ('BOX',           (0,0), (-1,-1), 0.5, ink_color),
                ('TOPPADDING',    (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LEFTPADDING',   (0,0), (-1,-1), 6),
                ('RIGHTPADDING',  (0,0), (-1,-1), 6),
                ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
                ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ]))

            claim_text  = safe(claim.get("claim", ""))
            evidence    = safe(claim.get("evidence", ""))
            text_content = [
                Paragraph(f'<b>{claim_text}</b>', S('claimtext')),
                Spacer(1, 2),
                Paragraph(
                    f'<font color="#6B7280"><i>Evidence: {evidence}</i></font>',
                    S('claimtext', fontSize=8.5, textColor=MUTED)
                ),
            ]

            row = Table(
                [[label_cell, text_content]],
                colWidths=[20*mm, CW - 20*mm]
            )
            row.setStyle(TableStyle([
                ('VALIGN',      (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (1,0), (1,0),   10),
                ('LEFTPADDING', (0,0), (0,0),   0),
                ('TOPPADDING',  (0,0), (-1,-1), 0),
            ]))
            flow.append(row)
            flow.append(Spacer(1, 8))

    flow.append(Spacer(1, 4))
    return flow


# ------------------------------------------------------------------
# SECTION 3: EXECUTIVE SUMMARY
# ------------------------------------------------------------------
def exec_summary_section(data):
    flow = section_header("02", "EXECUTIVE SUMMARY")

    exec_summary = data.get("executive_summary")
    if exec_summary:
        flow.append(Paragraph(safe(exec_summary), S('body')))
        flow.append(Spacer(1, 12))

    findings = data.get("key_findings", [])
    if findings:
        flow.append(Paragraph("Key Findings", S('h3')))
        for i, f in enumerate(findings, 1):
            flow.append(Paragraph(
                f'<font color="#8C1D2B"><b>{i:02d}</b></font>&nbsp;&nbsp;{safe(f)}',
                S('find')))
            flow.append(Spacer(1, 4))

    flow.append(Spacer(1, 12))
    return flow


# ------------------------------------------------------------------
# SECTION 4: MARKET & FINANCIAL ASSESSMENT
# ------------------------------------------------------------------
def market_financial_section(data):
    market_position = data.get("market_position")
    financial_health = data.get("financial_health")
    tam              = data.get("tam_estimate")
    competitors      = data.get("top_competitors")
    sentiment        = data.get("management_sentiment")
    mgmt_assessment  = data.get("management_assessment")

    if not (market_position or financial_health):
        return []

    flow = section_header("03", "MARKET & FINANCIAL ASSESSMENT")

    if market_position:
        flow.append(Paragraph("Market Position", S('h3')))
        flow.append(Paragraph(safe(market_position), S('body')))
        detail_parts = []
        if tam:
            detail_parts.append(f"Est. TAM: {safe(tam)}")
        if competitors:
            comp_str = ", ".join(
                safe(c) for c in competitors if c and c.lower() != "unknown"
            )
            if comp_str:
                detail_parts.append(f"Named competitors: {comp_str}")
        if detail_parts:
            flow.append(Spacer(1, 2))
            flow.append(Paragraph(
                "&nbsp;&nbsp;·&nbsp;&nbsp;".join(detail_parts), S('small')))
        flow.append(Spacer(1, 10))

    if financial_health:
        flow.append(Paragraph("Financial Health", S('h3')))
        flow.append(Paragraph(safe(financial_health), S('body')))
        flow.append(Spacer(1, 10))

    # Management
    flow.append(Paragraph("Management Assessment", S('h3')))
    if mgmt_assessment:
        flow.append(Paragraph(safe(mgmt_assessment), S('body')))
    if sentiment:
        color_hex = sentiment_color(sentiment)
        flow.append(Spacer(1, 4))
        flow.append(Paragraph(
            f'<font color="{color_hex}"><b>Overall sentiment: {safe(sentiment).upper()}</b></font>',
            S('body')))

    flow.append(Spacer(1, 12))
    return flow


# ------------------------------------------------------------------
# SECTION 5: SCORING & RISK PROFILE (charts)
# ------------------------------------------------------------------
def charts_section(data):
    scoring     = normalized_scoring(data)
    weakest_key = min(scoring, key=scoring.get)

    os.makedirs("data", exist_ok=True)
    radar_path = radar_chart(scoring)
    bars_path  = score_bars(scoring)

    flow = section_header("04", "SCORING & RISK PROFILE")

    risk_score = data.get("risk_score")
    if risk_score is not None:
        flow.append(Paragraph(
            f'<font color="#6B7280">Composite risk score: <b>{risk_score}/10</b> '
            f'(higher = more risk)</font>', S('small')))
        flow.append(Spacer(1, 4))

    insight = (
        f'<font color="#8C1D2B"><b>{SCORE_LABELS[weakest_key]}</b></font> is the weakest '
        f'dimension at {scoring[weakest_key]}/10 and the primary constraint on the overall score.'
    )
    flow.append(Paragraph(insight, S('body')))
    flow.append(Spacer(1, 10))

    radar_img = RLImage(radar_path, width=60*mm, height=60*mm)
    bars_img  = RLImage(bars_path, width=CW - 60*mm - 6, height=44*mm)
    t = Table([[radar_img, bars_img]], colWidths=[60*mm, CW - 60*mm])
    t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    flow += [t]
    return [KeepTogether(flow), Spacer(1, 16)]


# ------------------------------------------------------------------
# SECTION 6: RISK ASSESSMENT (flags + opportunities)
# ------------------------------------------------------------------
def flags_opps_section(data):
    flags = data.get("red_flags", [])
    opps  = data.get("opportunities", [])

    def item_text(it):
        return it.get("issue", str(it)) if isinstance(it, dict) else str(it)

    def column(items, heading, color_hex):
        items = items or ["None identified."]
        cells = [Paragraph(
            f'<font color="{color_hex}"><b>{heading}</b></font>', S('h3'))]
        cells.append(HRFlowable(
            width=(CW - 12) / 2, thickness=0.75, color=RULE,
            spaceBefore=2, spaceAfter=6))
        for it in items:
            cells.append(Paragraph(
                f'—&nbsp;&nbsp;{safe(item_text(it))}', S('flagtext')))
            cells.append(Spacer(1, 5))
        return cells

    left_col  = column(flags, "RED FLAGS",    "#8C1D2B")
    right_col = column(opps,  "OPPORTUNITIES","#2F6F4F")

    t = Table([[left_col, right_col]], colWidths=[(CW-12)/2, (CW-12)/2])
    t.setStyle(TableStyle([
        ('VALIGN',      (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (1,0), (1,0),   12),
        ('LEFTPADDING', (0,0), (0,0),   0),
    ]))
    flow = section_header("05", "RISK ASSESSMENT")
    flow += [t]
    return [KeepTogether(flow)]


# ------------------------------------------------------------------
# SECTION 7: UNANSWERED QUESTIONS (intellectual honesty)
# ------------------------------------------------------------------
def unanswered_section(data):
    questions = data.get("unanswered_questions", [])
    if not questions:
        return []

    flow = [Spacer(1, 16)]
    flow += section_header("06", "OPEN QUESTIONS FOR IC")
    flow.append(Paragraph(
        "These are critical questions this analysis cannot answer from public data alone. "
        "An Investment Committee should require answers before proceeding.",
        S('body', textColor=MUTED)))
    flow.append(Spacer(1, 10))

    for i, q in enumerate(questions, 1):
        flow.append(Paragraph(
            f'<font color="#8C1D2B"><b>Q{i}</b></font>&nbsp;&nbsp;{safe(q)}',
            S('unanswered')))
        flow.append(Spacer(1, 6))

    flow.append(Spacer(1, 12))
    return flow


# ------------------------------------------------------------------
# ASSEMBLY
# ------------------------------------------------------------------
def generate_report(data, output_path=None):
    company = safe(data.get("company", "Company")).strip() or "Company"
    if output_path is None:
        output_path = f"data/{company.replace(' ', '_')}_DD_Report.pdf"
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=24*mm, bottomMargin=16*mm
    )

    story = []
    story += cover_page(data, company)          # Cover: verdict badge + metrics
    story += verdict_thesis_section(data)       # 01: Deal thesis + traffic-light claims
    story += exec_summary_section(data)         # 02: Summary + key findings
    story += market_financial_section(data)     # 03: Market, financials, management
    story += charts_section(data)              # 04: Radar + score bars
    story += flags_opps_section(data)          # 05: Red flags vs opportunities
    story += unanswered_section(data)          # 06: Open IC questions

    chrome = partial(_chrome, company_label=company.upper())
    doc.build(story, onFirstPage=chrome, onLaterPages=chrome)
    return output_path


# ------------------------------------------------------------------
# TEST RUNNER
# ------------------------------------------------------------------
if __name__ == "__main__":
    company_name = input("Enter company name to test report: ").strip() or "Test Company"
    safe_name    = company_name.lower().replace(" ", "_")
    cached_path  = f"data/{safe_name}_analysis.json"

    if os.path.exists(cached_path):
        with open(cached_path, "r") as f:
            data = json.load(f)
    else:
        print(f"No cached analysis at {cached_path} — using sample data.")
        data = {
            "company": company_name,
            "founded_year": "2016",
            "total_raised": "$78M",
            "top_competitors": ["Northwind Robotics", "Vanta Systems", "Helix Dynamics"],
            "investment_verdict": "Hold",
            "verdict_reason": (
                "Three consecutive funding rounds and a recent enterprise contract win signal "
                "product-market fit; however, an unexplained founder departure in 2023 and "
                "no disclosed path to profitability make this a high-risk bet at current valuation."
            ),
            "deal_thesis": (
                f"{company_name} is a Hold because it has demonstrated repeatable revenue growth "
                "in a $4B niche, provided the founder succession risk is resolved before Series C close."
            ),
            "thesis_claims": [
                {
                    "claim": "Revenue growth is repeatable and not reliant on a single customer",
                    "status": "YELLOW",
                    "evidence": "3 enterprise wins announced in 12 months, but top customer not disclosed"
                },
                {
                    "claim": "Management team has the depth to execute post-Series B scale-up",
                    "status": "RED",
                    "evidence": "Co-founder departed Q3 2023 with no public explanation; replacement not announced"
                },
                {
                    "claim": "Competitive moat is durable beyond 24-month horizon",
                    "status": "GREEN",
                    "evidence": "2 patents filed in 2024, proprietary dataset cited in 4 press mentions"
                },
            ],
            "executive_summary": (
                f"{company_name} is a Hold. It has raised $78M across four rounds since 2016, "
                "most recently a $35M Series B in Q1 2024, implying 18-24 months of runway. "
                "Press coverage is net positive but an unexplained founder exit is the primary "
                "governance risk. An investor must verify the succession plan and customer "
                "concentration before proceeding."
            ),
            "market_position": (
                "Operates in robotics automation, a sector estimated at $4B TAM growing at ~14% CAGR. "
                "No disclosed market share; competes primarily on pricing rather than proprietary tech. "
                "Recent partnership with a Tier-1 distributor is the strongest moat signal."
            ),
            "tam_estimate": "$4.2B (robotics automation, 2024)",
            "financial_health": (
                "$78M raised across Seed, Series A, and Series B. Last round ($35M) closed Q1 2024. "
                "No revenue disclosed; estimated 18-24 months runway at typical Series B burn. "
                "No litigation or financial red flags in public record."
            ),
            "management_sentiment": "neutral",
            "management_assessment": (
                "Glassdoor rating of 3.8/5 with CEO approval at 72% — in line with sector median. "
                "Co-founder departure in 2023 is a yellow flag; no replacement announced as of data cutoff."
            ),
            "key_findings": [
                "$35M Series B in Q1 2024 suggests investor confidence, but implies ~18-month runway window.",
                "3 enterprise contracts announced in 12 months — repeatable sales motion, but concentration unknown.",
                "Co-founder exit (2023) is unresolved; governance risk is the primary IC concern.",
            ],
            "red_flags": [
                "Co-founder departed Q3 2023 without public explanation — succession risk unresolved.",
                "No disclosed revenue or path to profitability; valuation rest on funding momentum.",
            ],
            "opportunities": [
                "Adjacent market (warehouse automation, ~$2B) underserved — recent distributor deal opens the door.",
                "Proprietary dataset could be licensed as a SaaS product — 2 analyst mentions suggest market interest.",
            ],
            "unanswered_questions": [
                "What is the customer concentration — does the top 3 account for >40% of ARR?",
                "Why did the co-founder leave, and who is leading the Series C process?",
                "What is the current monthly burn rate and actual runway to cash-out?",
            ],
            "scoring": {
                "market_position": 6, "financial_health": 5,
                "management_quality": 5, "growth_potential": 7,
                "competitive_moat": 6,
            },
            "risk_score": 6,
            "confidence_level": "Low",
            "confidence_reason": (
                "Based on 28 public data points. No financial statements, management interviews, "
                "or proprietary data accessed. Directional signal only — not investment advice."
            ),
        }

    path = generate_report(data)
    print(f"Report generated: {path}")