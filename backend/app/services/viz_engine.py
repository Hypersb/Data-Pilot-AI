import json
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from app.services.ingest import infer_column_types


def generate_charts(df: pd.DataFrame) -> list[dict[str, Any]]:
    charts: list[dict[str, Any]] = []
    column_types = infer_column_types(df)

    numeric_cols = [c for c, t in column_types.items() if t == "numeric"]
    categorical_cols = [c for c, t in column_types.items() if t == "categorical"]
    datetime_cols = [c for c, t in column_types.items() if t == "datetime"]

    if datetime_cols and numeric_cols:
        charts.append(_line_chart(df, datetime_cols[0], numeric_cols[0]))

    if categorical_cols and numeric_cols:
        charts.append(_bar_chart(df, categorical_cols[0], numeric_cols[0]))

    if numeric_cols:
        charts.append(_histogram(df, numeric_cols[0]))

    if len(numeric_cols) >= 2:
        charts.append(_scatter(df, numeric_cols[0], numeric_cols[1]))

    if len(numeric_cols) >= 2:
        charts.append(_heatmap(df, numeric_cols))

    return [c for c in charts if c is not None]


def _fig_to_dict(fig: go.Figure) -> dict[str, Any]:
    return json.loads(pio.to_json(fig))


def _line_chart(df: pd.DataFrame, date_col: str, metric_col: str) -> dict[str, Any] | None:
    work = df[[date_col, metric_col]].copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work[metric_col] = pd.to_numeric(work[metric_col], errors="coerce")
    work = work.dropna().sort_values(date_col)
    if work.empty:
        return None

    grouped = work.groupby(date_col, as_index=False)[metric_col].sum()
    fig = px.line(grouped, x=date_col, y=metric_col, title=f"{metric_col} over time")
    return {
        "id": f"line_{date_col}_{metric_col}",
        "type": "line",
        "title": f"{metric_col} over time",
        "figure": _fig_to_dict(fig),
    }


def _bar_chart(df: pd.DataFrame, cat_col: str, metric_col: str) -> dict[str, Any] | None:
    work = df[[cat_col, metric_col]].copy()
    work[metric_col] = pd.to_numeric(work[metric_col], errors="coerce")
    grouped = work.groupby(cat_col, dropna=True)[metric_col].sum().reset_index()
    grouped = grouped.sort_values(metric_col, ascending=False).head(15)
    if grouped.empty:
        return None

    fig = px.bar(grouped, x=cat_col, y=metric_col, title=f"{metric_col} by {cat_col}")
    return {
        "id": f"bar_{cat_col}_{metric_col}",
        "type": "bar",
        "title": f"{metric_col} by {cat_col}",
        "figure": _fig_to_dict(fig),
    }


def _histogram(df: pd.DataFrame, col: str) -> dict[str, Any] | None:
    series = pd.to_numeric(df[col], errors="coerce").dropna()
    if series.empty:
        return None
    fig = px.histogram(x=series, title=f"Distribution of {col}", nbins=30)
    return {
        "id": f"hist_{col}",
        "type": "histogram",
        "title": f"Distribution of {col}",
        "figure": _fig_to_dict(fig),
    }


def _scatter(df: pd.DataFrame, col_x: str, col_y: str) -> dict[str, Any] | None:
    work = df[[col_x, col_y]].copy()
    work[col_x] = pd.to_numeric(work[col_x], errors="coerce")
    work[col_y] = pd.to_numeric(work[col_y], errors="coerce")
    work = work.dropna()
    if len(work) < 2:
        return None
    fig = px.scatter(work, x=col_x, y=col_y, title=f"{col_y} vs {col_x}")
    return {
        "id": f"scatter_{col_x}_{col_y}",
        "type": "scatter",
        "title": f"{col_y} vs {col_x}",
        "figure": _fig_to_dict(fig),
    }


def _heatmap(df: pd.DataFrame, numeric_cols: list[str]) -> dict[str, Any] | None:
    cols = numeric_cols[:8]
    numeric_df = df[cols].apply(pd.to_numeric, errors="coerce")
    corr = numeric_df.corr()
    if corr.isna().all().all():
        return None

    fig = px.imshow(
        corr,
        text_auto=".2f",
        title="Correlation heatmap",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
    )
    return {
        "id": "heatmap_correlation",
        "type": "heatmap",
        "title": "Correlation heatmap",
        "figure": _fig_to_dict(fig),
    }


def build_bar_chart_from_series(
    labels: list[str], values: list[float], title: str
) -> dict[str, Any]:
    fig = px.bar(x=labels, y=values, title=title, labels={"x": "Category", "y": "Value"})
    return _fig_to_dict(fig)
