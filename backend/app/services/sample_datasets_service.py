from __future__ import annotations

from typing import Any

import pandas as pd

from app.config import settings
from app.services.session_store import session_store

_SAMPLES_DIR = settings.resolved_samples_dir

SAMPLE_CATALOG: list[dict[str, Any]] = [
    {
        "id": "sales",
        "name": "Sales Analytics",
        "description": "Regional product revenue and units sold over time — ideal for forecasting and trend analysis.",
        "filename": "sales.csv",
        "task_hint": "forecasting",
    },
    {
        "id": "churn",
        "name": "Customer Churn",
        "description": "Subscription customer attributes and churn labels — classification and retention analysis.",
        "filename": "churn.csv",
        "task_hint": "classification",
    },
    {
        "id": "housing",
        "name": "Housing Prices",
        "description": "Property features and sale prices — regression and feature importance.",
        "filename": "housing.csv",
        "task_hint": "regression",
    },
    {
        "id": "marketing",
        "name": "Marketing Campaigns",
        "description": "Campaign spend, impressions, and conversions across channels.",
        "filename": "marketing.csv",
        "task_hint": "regression",
    },
    {
        "id": "netflix",
        "name": "Netflix Analytics",
        "description": "Content catalog with ratings, duration, and release year.",
        "filename": "netflix.csv",
        "task_hint": "exploration",
    },
    {
        "id": "pokemon",
        "name": "Pokemon Dataset",
        "description": "Pokemon stats, types, and combat attributes for comparative analysis.",
        "filename": "pokemon.csv",
        "task_hint": "classification",
    },
    {
        "id": "titanic",
        "name": "Titanic Dataset",
        "description": "Passenger demographics and survival outcomes — classic classification benchmark.",
        "filename": "titanic.csv",
        "task_hint": "classification",
    },
]


def list_samples() -> list[dict[str, Any]]:
    result = []
    for item in SAMPLE_CATALOG:
        path = _SAMPLES_DIR / item["filename"]
        rows, cols = 0, 0
        if path.is_file():
            try:
                df = pd.read_csv(path, nrows=5000)
                rows, cols = len(df), len(df.columns)
            except Exception:
                pass
        result.append({**item, "rows": rows, "columns": cols})
    return result


def load_sample(sample_id: str) -> dict[str, Any]:
    entry = next((s for s in SAMPLE_CATALOG if s["id"] == sample_id), None)
    if not entry:
        raise ValueError(f"Unknown sample dataset: {sample_id}")

    path = _SAMPLES_DIR / entry["filename"]
    if not path.is_file():
        raise ValueError(f"Sample file not found: {entry['filename']}")

    df = pd.read_csv(path)
    session_id = session_store.create(df, entry["filename"])
    preview = df.head(5).replace({pd.NA: None}).to_dict(orient="records")

    from app.services.ingest import infer_column_types

    return {
        "session_id": session_id,
        "filename": entry["filename"],
        "name": entry["name"],
        "rows": len(df),
        "columns": list(df.columns),
        "preview": preview,
        "column_types": infer_column_types(df),
    }
