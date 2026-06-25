from typing import Any

import numpy as np
import pandas as pd


def iqr_outlier_rate(series: pd.Series) -> float:
    if pd.api.types.is_bool_dtype(series):
        return 0.0
    clean = pd.to_numeric(series, errors="coerce").astype(float).dropna()
    if len(clean) < 10:
        return 0.0
    q1, q3 = clean.quantile(0.25), clean.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0.0
    outliers = clean[(clean < q1 - 1.5 * iqr) | (clean > q3 + 1.5 * iqr)]
    return round(len(outliers) / len(clean) * 100, 2)


def aggregate_outlier_rate(df: pd.DataFrame, numeric_cols: list[str]) -> float:
    if not numeric_cols:
        return 100.0
    rates = [iqr_outlier_rate(df[col]) for col in numeric_cols[:10]]
    avg_rate = sum(rates) / len(rates)
    return round(max(0.0, 100.0 - avg_rate * 2), 2)


def count_outliers_per_column(df: pd.DataFrame, numeric_cols: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for col in numeric_cols[:10]:
        clean = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(clean) < 10:
            continue
        q1, q3 = clean.quantile(0.25), clean.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        mask = (clean < q1 - 1.5 * iqr) | (clean > q3 + 1.5 * iqr)
        result[col] = int(mask.sum())
    return result
