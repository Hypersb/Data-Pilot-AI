import asyncio
from typing import Any

import pandas as pd

from app.agents.business_consultant_agent import run_business_consultant
from app.agents.data_analyst_agent import run_data_analyst
from app.agents.ml_engineer_agent import run_ml_engineer
from app.agents.qa_auditor_agent import run_qa_auditor


async def run_team_analysis(df: pd.DataFrame, session_id: str = "") -> dict[str, Any]:
    loop = asyncio.get_event_loop()

    analyst = await loop.run_in_executor(None, run_data_analyst, df)
    ml = await loop.run_in_executor(None, run_ml_engineer, df, session_id)
    qa = await loop.run_in_executor(None, run_qa_auditor, df)
    business = await run_business_consultant(df)

    combined_recs: list[str] = []
    for section in (qa, business, analyst):
        for f in section["findings"]:
            if any(kw in f.lower() for kw in ("recommend", "action", "apply", "should", "review")):
                combined_recs.append(f)
    if not combined_recs:
        combined_recs = business["findings"][-1:] if business["findings"] else ["Validate findings with domain experts."]

    executive = (
        f"Multi-agent analysis complete. QA score: {qa['findings'][0]}. "
        f"{analyst['findings'][0] if analyst['findings'] else ''} "
        f"{business['findings'][0] if business['findings'] else ''}"
    ).strip()

    return {
        "executive_summary": executive,
        "analyst_section": analyst,
        "ml_section": ml,
        "business_section": business,
        "qa_section": qa,
        "combined_recommendations": combined_recs[:8],
    }
