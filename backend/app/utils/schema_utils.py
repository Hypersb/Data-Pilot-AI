from typing import Any

import pandas as pd

from app.services.ingest import infer_column_types


def detect_column_roles(df: pd.DataFrame) -> dict[str, str]:
    """Classify columns as metric, dimension, date, id, or text."""
    types = infer_column_types(df)
    roles: dict[str, str] = {}
    for col in df.columns:
        col_type = types[col]
        series = df[col]
        unique = series.nunique(dropna=True)
        n = len(df)

        if col_type == "datetime":
            roles[col] = "date"
        elif col_type == "numeric":
            roles[col] = "metric"
        elif unique == n and unique > 0:
            roles[col] = "id"
        elif col_type == "categorical" and unique <= max(50, int(n * 0.2)):
            roles[col] = "dimension"
        else:
            roles[col] = "text"
    return roles


def pick_metric_column(df: pd.DataFrame, requested: str | None = None) -> str | None:
    roles = detect_column_roles(df)
    if requested and requested in df.columns:
        return requested
    metrics = [c for c, r in roles.items() if r == "metric"]
    if not metrics:
        return None
    variances = {c: pd.to_numeric(df[c], errors="coerce").var() for c in metrics}
    return max(variances, key=lambda c: variances[c] or 0)


def pick_date_column(df: pd.DataFrame, requested: str | None = None) -> str | None:
    roles = detect_column_roles(df)
    if requested and requested in df.columns:
        return requested
    dates = [c for c, r in roles.items() if r == "date"]
    if dates:
        return dates[0]
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            return col
    return None


def pick_dimension_columns(df: pd.DataFrame, requested: list[str] | None = None) -> list[str]:
    if requested:
        return [c for c in requested if c in df.columns]
    roles = detect_column_roles(df)
    return [c for c, r in roles.items() if r == "dimension"][:5]


def align_schemas(df_a: pd.DataFrame, df_b: pd.DataFrame) -> dict[str, Any]:
    cols_a = set(df_a.columns)
    cols_b = set(df_b.columns)
    common = sorted(cols_a & cols_b)
    only_a = sorted(cols_a - cols_b)
    only_b = sorted(cols_b - cols_a)
    types_a = infer_column_types(df_a)
    types_b = infer_column_types(df_b)
    type_mismatches = [
        {"column": c, "type_a": types_a[c], "type_b": types_b[c]}
        for c in common
        if types_a.get(c) != types_b.get(c)
    ]
    return {
        "common_columns": common,
        "only_in_a": only_a,
        "only_in_b": only_b,
        "type_mismatches": type_mismatches,
    }
