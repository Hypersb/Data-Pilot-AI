import io
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer
from pptx import Presentation
from pptx.util import Pt

from app.services.dashboard_service import generate_dashboard
from app.services.forecast_engine import run_forecast_leaderboard
from app.services.health_score_service import compute_health_score
from app.services.insight_engine import generate_insights
from app.services.report_engine import generate_report
from app.services.storytelling_service import generate_story

_LOGO_CANDIDATES = [
    Path(__file__).resolve().parent.parent.parent.parent / "assets" / "logo.png",
    Path(__file__).resolve().parent.parent.parent / "assets" / "logo.png",
]


async def generate_full_report(
    df: pd.DataFrame,
    filename: str,
    fmt: Literal["markdown", "pdf", "pptx"] = "markdown",
) -> dict[str, Any]:
    base = await generate_report(df, filename)
    health = compute_health_score(df)
    insights = generate_insights(df)
    story = await generate_story(df)
    dashboard = generate_dashboard(df)

    forecast_outlook = "Forecast not available for this dataset."
    try:
        fc = run_forecast_leaderboard(df, forecast_horizon=6)
        if fc.get("available") and fc.get("forecast"):
            next_val = fc["forecast"][0]["value"]
            forecast_outlook = (
                f"Best model: {fc['best_model']['model_name']}. "
                f"Next period forecast for {fc['target_column']}: {next_val:,.2f}. "
                f"{fc.get('explanation', '')}"
            )
    except ValueError:
        pass

    key_findings = [i["description"] for i in insights[:5]]
    risks = [i["description"] for i in insights if i["severity"] == "high"][:5]
    if not risks and health["overall_score"] < 60:
        risks = [f"Data quality score is {health['overall_score']}/100."]
    opportunities = [
        i["description"] for i in insights
        if i["type"] in ("growth", "category_performance", "trend")
    ][:5]
    recommendations = health.get("recommended_fixes", [])[:5]
    recommendations.extend(story["what_to_do_next"].split(". ")[:2])
    recommendations = [r.strip() for r in recommendations if r.strip()][:8]

    executive_summary = (
        f"Analysis of '{filename}' ({health['rows']} rows, {health['columns']} columns). "
        f"Health score: {health['overall_score']}/100. "
        f"{story['what_happened']}"
    )

    result: dict[str, Any] = {
        "markdown": base["markdown"],
        "executive_summary": executive_summary,
        "key_findings": key_findings,
        "risks": risks,
        "opportunities": opportunities,
        "recommendations": recommendations,
        "forecast_outlook": forecast_outlook,
        "llm_enhanced": base.get("llm_enhanced", False),
        "format": fmt,
    }

    if fmt == "pdf":
        result["file_bytes"] = _build_pdf(
            executive_summary,
            key_findings,
            forecast_outlook,
            risks,
            opportunities,
            recommendations,
            dashboard.get("kpis", []),
        )
    elif fmt == "pptx":
        result["file_bytes"] = _build_pptx(
            filename, executive_summary, key_findings, risks, opportunities, recommendations
        )

    return result


def _logo_path() -> Path | None:
    for path in _LOGO_CANDIDATES:
        if path.is_file():
            return path
    return None


def _build_pdf(
    summary: str,
    findings: list[str],
    forecast_outlook: str,
    risks: list[str],
    opportunities: list[str],
    recommendations: list[str],
    kpis: list[dict[str, Any]],
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story: list[Any] = []

    logo = _logo_path()
    if logo:
        story.append(Image(str(logo), width=1.2 * inch, height=1.2 * inch))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Prisma AI — Business Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Executive Summary</b>", styles["Heading2"]))
    story.append(Paragraph(summary, styles["Normal"]))
    story.append(Spacer(1, 12))

    if kpis:
        story.append(Paragraph("<b>Key Metrics</b>", styles["Heading2"]))
        for k in kpis[:4]:
            story.append(
                Paragraph(
                    f"• {k.get('label', k.get('column'))}: {k.get('value', 0):,.2f}",
                    styles["Normal"],
                )
            )
        story.append(Spacer(1, 8))

    sections = [
        ("Key Findings", findings),
        ("Forecast Outlook", [forecast_outlook]),
        ("Risks", risks),
        ("Opportunities", opportunities),
        ("Recommendations", recommendations),
    ]
    for title, items in sections:
        story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        for item in items or ["None identified."]:
            story.append(Paragraph(f"• {item}", styles["Normal"]))
        story.append(Spacer(1, 8))

    doc.build(story)
    return buffer.getvalue()


def _build_pptx(
    filename: str,
    summary: str,
    findings: list[str],
    risks: list[str],
    opportunities: list[str],
    recommendations: list[str],
) -> bytes:
    prs = Presentation()
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = "Executive Report"
    title_slide.placeholders[1].text = filename

    sections = [
        ("Executive Summary", [summary]),
        ("Key Findings", findings),
        ("Risks", risks),
        ("Opportunities", opportunities),
        ("Recommendations", recommendations),
    ]

    for section_title, bullets in sections:
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = section_title
        body = slide.placeholders[1].text_frame
        body.clear()
        for i, bullet in enumerate(bullets or ["None identified."]):
            p = body.paragraphs[0] if i == 0 else body.add_paragraph()
            p.text = bullet
            p.font.size = Pt(14)

    buffer = io.BytesIO()
    prs.save(buffer)
    return buffer.getvalue()
