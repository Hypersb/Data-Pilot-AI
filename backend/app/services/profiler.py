from typing import Any

import numpy as np
import pandas as pd

from app.services.ingest import infer_column_types


def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    column_types = infer_column_types(df)
    columns_info: list[dict[str, Any]] = []
    quality_flags: list[str] = []

    duplicate_rows = int(df.duplicated().sum())
    total_rows = len(df)
    total_cols = len(df.columns)

    for col in df.columns:
        series = df[col]
        null_count = int(series.isna().sum())
        null_pct = round(null_count / total_rows * 100, 2) if total_rows else 0
        unique_count = int(series.nunique(dropna=True))
        col_type = column_types[col]

        info: dict[str, Any] = {
            "name": col,
            "dtype": col_type,
            "null_count": null_count,
            "null_pct": null_pct,
            "unique_count": unique_count,
        }

        if null_pct > 20:
            quality_flags.append(f"Column '{col}' has {null_pct}% missing values.")
        if unique_count == 1 and null_count < total_rows:
            quality_flags.append(f"Column '{col}' is constant.")

        if col_type == "numeric":
            clean = pd.to_numeric(series, errors="coerce")
            info.update(
                {
                    "min": _safe_float(clean.min()),
                    "max": _safe_float(clean.max()),
                    "mean": _safe_float(clean.mean()),
                    "std": _safe_float(clean.std()),
                }
            )
        elif col_type == "categorical":
            top = series.value_counts().head(3)
            info["top_values"] = [
                {"value": str(k), "count": int(v)} for k, v in top.items()
            ]

        columns_info.append(info)

    missing_cells = int(df.isna().sum().sum())
    total_cells = total_rows * total_cols if total_cols else 0
    completeness = round((1 - missing_cells / total_cells) * 100, 2) if total_cells else 100

    quality_score = max(0, min(100, round(completeness - len(quality_flags) * 3)))

    return {
        "rows": total_rows,
        "columns": total_cols,
        "duplicate_rows": duplicate_rows,
        "missing_cells": missing_cells,
        "completeness_pct": completeness,
        "quality_score": quality_score,
        "quality_flags": quality_flags[:10],
        "columns_info": columns_info,
        "column_types": column_types,
    }


def _safe_float(val: Any) -> float | None:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    return round(float(val), 4)
