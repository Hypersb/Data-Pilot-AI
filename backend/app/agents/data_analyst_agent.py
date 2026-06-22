from typing import Any

import pandas as pd

from app.services.comparison_service import compare_periods
from app.services.insight_engine import generate_insights
from app.services.root_cause_service import analyze_root_cause
from app.utils.schema_utils import pick_metric_column


def run_data_analyst(df: pd.DataFrame) -> dict[str, Any]:
    insights = generate_insights(df)
    findings: list[str] = [i["description"] for i in insights[:6]]
    citations = [i["title"] for i in insights[:6]]

    metric = pick_metric_column(df)
    if metric:
        try:
            rc = analyze_root_cause(df, metric)
            findings.insert(0, f"{metric} changed {rc['metric_change_pct']:+.1f}% across periods.")
            citations.append("root_cause_analysis")
        except ValueError:
            pass
        try:
            comp = compare_periods(df, metric_column=metric)
            if comp["changes"]:
                latest = comp["changes"][-1]
                findings.append(f"Latest period change: {latest['change_pct']:+.1f}%.")
                citations.append("period_comparison")
        except ValueError:
            pass

    return {
        "role": "data_analyst",
        "findings": findings or ["No significant trends detected."],
        "confidence": 0.88 if findings else 0.5,
        "citations": citations,
    }
