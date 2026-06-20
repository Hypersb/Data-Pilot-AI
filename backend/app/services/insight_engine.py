from typing import Any

import numpy as np
import pandas as pd

from app.services.ingest import infer_column_types


def generate_insights(df: pd.DataFrame) -> list[dict[str, Any]]:
    insights: list[dict[str, Any]] = []
    column_types = infer_column_types(df)

    numeric_cols = [c for c, t in column_types.items() if t == "numeric"]
    categorical_cols = [c for c, t in column_types.items() if t == "categorical"]
    datetime_cols = [c for c, t in column_types.items() if t == "datetime"]

    insights.extend(_correlation_insights(df, numeric_cols))
    insights.extend(_outlier_insights(df, numeric_cols))
    insights.extend(_category_performance_insights(df, categorical_cols, numeric_cols))
    insights.extend(_trend_insights(df, datetime_cols, numeric_cols))
    insights.extend(_growth_insights(df, datetime_cols, numeric_cols))

    severity_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    insights.sort(key=lambda x: severity_order.get(x["severity"], 4))
    return insights


def _correlation_insights(df: pd.DataFrame, numeric_cols: list[str]) -> list[dict[str, Any]]:
    if len(numeric_cols) < 2:
        return []

    numeric_df = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    corr = numeric_df.corr()
    insights = []

    for i, col_a in enumerate(numeric_cols):
        for col_b in numeric_cols[i + 1 :]:
            r = corr.loc[col_a, col_b]
            if pd.isna(r) or abs(r) < 0.7:
                continue
            direction = "positive" if r > 0 else "negative"
            insights.append(
                {
                    "type": "correlation",
                    "title": f"Strong {direction} correlation",
                    "description": f"'{col_a}' and '{col_b}' have a {direction} correlation (r={r:.2f}).",
                    "severity": "medium" if abs(r) < 0.85 else "high",
                    "related_columns": [col_a, col_b],
                }
            )
    return insights


def _outlier_insights(df: pd.DataFrame, numeric_cols: list[str]) -> list[dict[str, Any]]:
    insights = []
    for col in numeric_cols[:5]:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(series) < 10:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        outliers = series[(series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)]
        if len(outliers) == 0:
            continue
        pct = round(len(outliers) / len(series) * 100, 1)
        insights.append(
            {
                "type": "outlier",
                "title": f"Outliers detected in '{col}'",
                "description": f"{len(outliers)} outliers ({pct}% of values) found using IQR method.",
                "severity": "medium" if pct < 5 else "high",
                "related_columns": [col],
            }
        )
    return insights


def _category_performance_insights(
    df: pd.DataFrame, categorical_cols: list[str], numeric_cols: list[str]
) -> list[dict[str, Any]]:
    if not categorical_cols or not numeric_cols:
        return []

    insights = []
    cat_col = categorical_cols[0]
    metric_col = numeric_cols[0]
    grouped = (
        df.groupby(cat_col, dropna=True)[metric_col]
        .apply(lambda s: pd.to_numeric(s, errors="coerce").sum())
        .sort_values(ascending=False)
    )
    if grouped.empty:
        return []

    top = grouped.index[0]
    top_val = grouped.iloc[0]
    insights.append(
        {
            "type": "category_performance",
            "title": f"Top performer: {top}",
            "description": f"'{top}' leads in '{metric_col}' with total {top_val:,.2f}.",
            "severity": "info",
            "related_columns": [cat_col, metric_col],
        }
    )

    if len(grouped) > 1:
        bottom = grouped.index[-1]
        bottom_val = grouped.iloc[-1]
        insights.append(
            {
                "type": "category_performance",
                "title": f"Lowest performer: {bottom}",
                "description": f"'{bottom}' has the lowest '{metric_col}' at {bottom_val:,.2f}.",
                "severity": "low",
                "related_columns": [cat_col, metric_col],
            }
        )
    return insights


def _trend_insights(
    df: pd.DataFrame, datetime_cols: list[str], numeric_cols: list[str]
) -> list[dict[str, Any]]:
    if not datetime_cols or not numeric_cols:
        return []

    date_col = datetime_cols[0]
    metric_col = numeric_cols[0]
    work = df[[date_col, metric_col]].copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work[metric_col] = pd.to_numeric(work[metric_col], errors="coerce")
    work = work.dropna().sort_values(date_col)

    if len(work) < 5:
        return []

    x = np.arange(len(work))
    y = work[metric_col].values
    slope = np.polyfit(x, y, 1)[0]
    direction = "upward" if slope > 0 else "downward"
    insights = [
        {
            "type": "trend",
            "title": f"{direction.capitalize()} trend in '{metric_col}'",
            "description": f"'{metric_col}' shows a {direction} trend over '{date_col}'.",
            "severity": "info",
            "related_columns": [date_col, metric_col],
        }
    ]
    return insights


def _growth_insights(
    df: pd.DataFrame, datetime_cols: list[str], numeric_cols: list[str]
) -> list[dict[str, Any]]:
    if not datetime_cols or not numeric_cols:
        return []

    date_col = datetime_cols[0]
    metric_col = numeric_cols[0]
    work = df[[date_col, metric_col]].copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work[metric_col] = pd.to_numeric(work[metric_col], errors="coerce")
    work = work.dropna().sort_values(date_col)

    if len(work) < 2:
        return []

    first = work[metric_col].iloc[0]
    last = work[metric_col].iloc[-1]
    if first == 0:
        return []

    change_pct = round((last - first) / abs(first) * 100, 2)
    direction = "growth" if change_pct > 0 else "decline"
    insights = [
        {
            "type": "growth",
            "title": f"Overall {direction} of {abs(change_pct)}%",
            "description": f"'{metric_col}' changed from {first:,.2f} to {last:,.2f} ({change_pct:+.2f}%).",
            "severity": "medium" if abs(change_pct) > 20 else "info",
            "related_columns": [date_col, metric_col],
        }
    ]
    return insights
