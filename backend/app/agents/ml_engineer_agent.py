from typing import Any

import pandas as pd

from app.services.automl_engine import run_automl
from app.services.experiment_tracker_service import experiment_tracker
from app.services.forecast_engine import run_forecast_leaderboard
from app.services.xai_engine import run_xai_explanation


def run_ml_engineer(df: pd.DataFrame, session_id: str = "") -> dict[str, Any]:
    findings: list[str] = []
    citations: list[str] = []

    try:
        automl = run_automl(df)
        best = automl["best_model"]
        findings.append(
            f"AutoML best model: {best['model_name']} ({automl['task_type']}) "
            f"with metrics {best['metrics']}."
        )
        citations.append("automl")
        if session_id:
            experiment_tracker.log_run(
                session_id=session_id,
                model_name=best["model_name"],
                task_type=automl["task_type"],
                metrics=best["metrics"],
                notes="Logged by ml_engineer_agent",
            )
    except (ValueError, Exception) as exc:
        findings.append(f"AutoML unavailable: {exc}")

    try:
        fc = run_forecast_leaderboard(df, forecast_horizon=6)
        if fc.get("available"):
            best = fc["best_model"]
            findings.append(
                f"Forecast best model: {best['model_name']} for {fc['target_column']}."
            )
            citations.append("forecast")
    except (ValueError, Exception):
        pass

    try:
        xai = run_xai_explanation(df)
        if xai.get("available") and xai.get("top_features"):
            top = xai["top_features"][0]
            findings.append(f"Top SHAP driver: {top['display_name']} (importance {top['importance']:.3f}).")
            citations.append("xai")
    except (ValueError, Exception):
        pass

    return {
        "role": "ml_engineer",
        "findings": findings or ["ML analysis could not be completed on this dataset."],
        "confidence": 0.85 if len(findings) > 1 else 0.6,
        "citations": citations,
    }
