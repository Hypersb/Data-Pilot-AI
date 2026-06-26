from typing import Any

import pandas as pd

from app.services.health_score_service import compute_health_score
from app.services.ingest import infer_column_types
from app.services.viz_engine import generate_charts
from app.utils.schema_utils import detect_column_roles


def generate_dashboard(df: pd.DataFrame) -> dict[str, Any]:
    roles = detect_column_roles(df)
    column_types = infer_column_types(df)
    health = compute_health_score(df)

    kpis: list[dict[str, Any]] = []
    numeric_cols = [c for c, r in roles.items() if r == "metric"]
    for col in numeric_cols[:4]:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(series) == 0:
            continue
        agg = "sum" if any(k in col.lower() for k in ("revenue", "sales", "amount", "total")) else "mean"
        value = float(series.sum()) if agg == "sum" else float(series.mean())
        if value != value:  # NaN
            continue
        kpis.append(
            {
                "label": col.replace("_", " ").title(),
                "column": col,
                "aggregation": agg,
                "value": round(value, 2),
                "format": "currency" if "revenue" in col.lower() or "amount" in col.lower() else "number",
            }
        )

    charts = generate_charts(df)
    chart_data = {c["id"]: c["figure"] for c in charts}
    panels = [
        {
            "id": c["id"],
            "type": c["type"],
            "title": c["title"],
            "chart_id": c["id"],
            "config": {},
        }
        for c in charts
    ]

    quality_alerts = [i["description"] for i in health["issues"][:5]]

    return {
        "kpis": kpis,
        "panels": panels,
        "quality_alerts": quality_alerts,
        "chart_data": chart_data,
    }
