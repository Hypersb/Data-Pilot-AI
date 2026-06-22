from typing import Any

import pandas as pd

from app.services.insight_engine import generate_insights
from app.services.storytelling_service import generate_story


async def run_business_consultant(df: pd.DataFrame) -> dict[str, Any]:
    story = await generate_story(df)
    insights = generate_insights(df)
    rec_insights = [i for i in insights if i["severity"] in ("high", "medium")][:3]

    findings = [
        story["what_happened"],
        story["why_it_happened"],
        story["what_to_do_next"],
    ]
    for ins in rec_insights:
        findings.append(f"Action item: {ins['description']}")

    return {
        "role": "business_consultant",
        "findings": findings,
        "confidence": 0.82,
        "citations": story.get("facts", [])[:5],
    }
