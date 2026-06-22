from typing import Any

import pandas as pd

from app.services.health_score_service import compute_health_score
from app.services.insight_engine import generate_insights
from app.services.root_cause_service import analyze_root_cause
from app.utils.narrative_utils import build_executive_paragraph, format_pct_change
from app.utils.schema_utils import pick_metric_column


async def generate_story(df: pd.DataFrame, topic: str | None = None) -> dict[str, Any]:
    health = compute_health_score(df)
    insights = generate_insights(df)
    facts: list[str] = []

    metric_col = pick_metric_column(df, topic if topic and topic in df.columns else None)
    root_cause_data: dict[str, Any] | None = None
    if metric_col:
        try:
            root_cause_data = analyze_root_cause(df, metric_col)
        except ValueError:
            pass

    growth_insights = [i for i in insights if i["type"] in ("growth", "trend", "category_performance")]
    what_bullets: list[str] = []
    why_bullets: list[str] = []
    next_bullets: list[str] = []

    if root_cause_data:
        pct = root_cause_data["metric_change_pct"]
        facts.append(
            f"{metric_col} {format_pct_change(pct)} "
            f"(delta: {root_cause_data['total_delta']:,.2f})."
        )
        what_bullets.append(
            f"{metric_col.replace('_', ' ').title()} {format_pct_change(pct)} "
            f"from {root_cause_data['baseline_total']:,.2f} to {root_cause_data['comparison_total']:,.2f}."
        )
        top_contrib = root_cause_data["contributors"][:3]
        for c in top_contrib:
            why_bullets.append(
                f"{c['dimension']} '{c['value']}' contributed {c['contribution_pct']:.1f}% "
                f"({c['delta']:+,.2f})."
            )
            facts.append(
                f"{c['dimension']}={c['value']}: contribution {c['contribution_pct']:.1f}%."
            )

    for ins in growth_insights[:3]:
        what_bullets.append(ins["description"])
        facts.append(ins["description"])

    if health["overall_score"] < 70:
        why_bullets.append(f"Data quality score is {health['overall_score']}/100, which may affect reliability.")
        facts.append(f"Health score: {health['overall_score']}/100.")

    for fix in health.get("recommended_fixes", [])[:3]:
        next_bullets.append(f"Apply cleaning operation: {fix.replace('_', ' ')}.")

    high_insights = [i for i in insights if i["severity"] in ("high", "medium")][:2]
    for ins in high_insights:
        next_bullets.append(ins["description"])

    if not next_bullets:
        next_bullets.append("Continue monitoring key metrics and validate findings with domain experts.")

    llm_enhanced = False
    what = build_executive_paragraph(what_bullets) if what_bullets else "No significant metric changes detected in the dataset."
    why = build_executive_paragraph(why_bullets) if why_bullets else "Insufficient dimensional breakdown available."
    nxt = build_executive_paragraph(next_bullets)

    return {
        "what_happened": what,
        "why_it_happened": why,
        "what_to_do_next": nxt,
        "facts": facts,
        "llm_enhanced": llm_enhanced,
    }
