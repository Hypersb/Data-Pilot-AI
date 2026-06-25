from typing import Any

import pandas as pd

from app.services.dashboard_service import generate_dashboard
from app.services.forecast_engine import run_forecast_leaderboard
from app.services.insight_engine import generate_insights
from app.services.profiler import profile_dataframe


def build_analysis_bundle(df: pd.DataFrame) -> dict[str, Any]:
    profile = profile_dataframe(df)
    insights = generate_insights(df)
    try:
        dashboard = generate_dashboard(df)
    except Exception as exc:
        dashboard = {
            "kpis": [],
            "panels": [],
            "quality_alerts": [f"Dashboard unavailable: {exc}"],
            "chart_data": {},
        }

    forecast: dict[str, Any] | None = None
    forecast_available = False
    forecast_message = "Forecast not available for this dataset."
    try:
        fc = run_forecast_leaderboard(df, forecast_horizon=6)
        if fc.get("available"):
            forecast = fc
            forecast_available = True
            forecast_message = fc.get("explanation", "Forecast generated successfully.")
    except ValueError as exc:
        forecast_message = str(exc)

    return {
        "profile": profile,
        "insights": insights,
        "insight_count": len(insights),
        "dashboard": {
            "kpis": dashboard["kpis"],
            "panels": dashboard["panels"],
            "quality_alerts": dashboard["quality_alerts"],
            "chart_data": dashboard["chart_data"],
        },
        "forecast_available": forecast_available,
        "forecast_message": forecast_message,
        "forecast": forecast,
    }
