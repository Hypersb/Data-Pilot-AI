from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from sklearn.ensemble import IsolationForest

from app.services.ingest import infer_column_types

FALLBACK_MESSAGE = "Anomaly detection is not available for this dataset."
MIN_ROWS = 5
MIN_ROWS_ISOLATION = 10
MIN_ROWS_TIMESERIES = 8
ZSCORE_THRESHOLD = 3.0


def detect_anomalies(df: pd.DataFrame) -> dict[str, Any]:
    try:
        return _detect_anomalies(df)
    except Exception:
        return _fallback_response()


def _detect_anomalies(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty or len(df) < MIN_ROWS:
        return _fallback_response("Dataset is too small for anomaly detection.")

    column_types = infer_column_types(df)
    numeric_cols = [c for c, t in column_types.items() if t == "numeric"]
    datetime_cols = [c for c, t in column_types.items() if t == "datetime"]

    if not numeric_cols:
        return _fallback_response("No numeric columns found for anomaly detection.")

    methods_used: list[str] = []
    row_hits: dict[int, dict[str, Any]] = {}

    iqr_flags = _detect_iqr(df, numeric_cols)
    if iqr_flags:
        methods_used.append("IQR")
        _merge_flags(row_hits, iqr_flags)

    zscore_flags = _detect_zscore(df, numeric_cols)
    if zscore_flags:
        methods_used.append("Z-score")
        _merge_flags(row_hits, zscore_flags)

    iso_flags = _detect_isolation_forest(df, numeric_cols)
    if iso_flags:
        methods_used.append("Isolation Forest")
        _merge_flags(row_hits, iso_flags)

    if datetime_cols:
        ts_flags = _detect_timeseries(df, datetime_cols[0], numeric_cols)
        if ts_flags:
            methods_used.append("Time-series")
            _merge_flags(row_hits, ts_flags)

    if not methods_used:
        return {
            "available": True,
            "total_anomalies": 0,
            "anomaly_methods_used": [],
            "anomaly_rows": [],
            "anomaly_summary": "No anomalies detected in this dataset.",
            "top_anomalous_columns": [],
            "severity_score": 0.0,
            "plain_english_explanation": "No unusual rows or values were detected.",
            "chart_data": _build_chart_data(df, [], numeric_cols, datetime_cols),
        }

    anomaly_rows = _build_anomaly_rows(df, row_hits)
    top_columns = _top_anomalous_columns(row_hits)
    total = len(anomaly_rows)
    severity = _severity_score(total, len(df), methods_used)
    summary = _anomaly_summary(total, top_columns, methods_used)
    explanation = _plain_english_explanation(total, top_columns, methods_used)

    return {
        "available": True,
        "total_anomalies": total,
        "anomaly_methods_used": methods_used,
        "anomaly_rows": anomaly_rows,
        "anomaly_summary": summary,
        "top_anomalous_columns": top_columns,
        "severity_score": severity,
        "plain_english_explanation": explanation,
        "chart_data": _build_chart_data(df, anomaly_rows, numeric_cols, datetime_cols),
    }


def _fallback_response(message: str = FALLBACK_MESSAGE) -> dict[str, Any]:
    return {
        "available": False,
        "total_anomalies": 0,
        "anomaly_methods_used": [],
        "anomaly_rows": [],
        "anomaly_summary": message,
        "top_anomalous_columns": [],
        "severity_score": 0.0,
        "plain_english_explanation": message,
        "chart_data": {},
    }


def _detect_iqr(df: pd.DataFrame, numeric_cols: list[str]) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors="coerce")
        valid = series.dropna()
        if len(valid) < MIN_ROWS:
            continue
        q1, q3 = valid.quantile(0.25), valid.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask = (series < lower) | (series > upper)
        for idx in series[mask.fillna(False)].index:
            value = float(series.loc[idx])
            direction = "much higher than normal" if value > upper else "much lower than normal"
            flags.append(
                {
                    "row_index": int(idx),
                    "column": col,
                    "method": "IQR",
                    "value": round(value, 4),
                    "direction": direction,
                }
            )
    return flags


def _detect_zscore(df: pd.DataFrame, numeric_cols: list[str]) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors="coerce")
        valid = series.dropna()
        if len(valid) < MIN_ROWS:
            continue
        median = valid.median()
        mad = np.median(np.abs(valid - median))
        if mad == 0:
            mad = float(valid.std())
        if mad == 0 or pd.isna(mad):
            continue
        modified_z = 0.6745 * (series - median) / mad
        mask = modified_z.abs() >= 3.5
        for idx in series[mask.fillna(False)].index:
            value = float(series.loc[idx])
            direction = "much higher than normal" if modified_z.loc[idx] > 0 else "much lower than normal"
            flags.append(
                {
                    "row_index": int(idx),
                    "column": col,
                    "method": "Z-score",
                    "value": round(value, 4),
                    "direction": direction,
                }
            )
    return flags


def _detect_isolation_forest(df: pd.DataFrame, numeric_cols: list[str]) -> list[dict[str, Any]]:
    if len(df) < MIN_ROWS_ISOLATION:
        return []

    matrix = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    matrix = matrix.dropna(how="all")
    if len(matrix) < MIN_ROWS_ISOLATION:
        return []

    filled = matrix.copy()
    for col in filled.columns:
        filled[col] = filled[col].fillna(filled[col].median())

    model = IsolationForest(contamination=min(0.05, max(0.02, 5 / len(filled))), random_state=42)
    labels = model.fit_predict(filled)
    scores = model.decision_function(filled)

    flags: list[dict[str, Any]] = []
    for i, (idx, label) in enumerate(zip(filled.index, labels)):
        if label != -1:
            continue
        deviations = (filled.iloc[i] - filled.median()).abs()
        worst_col = deviations.idxmax()
        flags.append(
            {
                "row_index": int(idx),
                "column": str(worst_col),
                "method": "Isolation Forest",
                "value": round(float(filled.iloc[i][worst_col]), 4),
                "direction": "outside the expected multivariate range",
                "score": round(float(scores[i]), 4),
            }
        )
    return flags


def _detect_timeseries(
    df: pd.DataFrame, date_col: str, numeric_cols: list[str]
) -> list[dict[str, Any]]:
    work = df.copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work = work.dropna(subset=[date_col]).sort_values(date_col)
    if len(work) < MIN_ROWS_TIMESERIES:
        return []

    flags: list[dict[str, Any]] = []
    for col in numeric_cols[:5]:
        series = pd.to_numeric(work[col], errors="coerce")
        if series.dropna().shape[0] < MIN_ROWS_TIMESERIES:
            continue
        rolling_mean = series.rolling(window=3, min_periods=2).mean()
        rolling_std = series.rolling(window=3, min_periods=2).std().replace(0, np.nan)
        z = (series - rolling_mean) / rolling_std
        mask = z.abs() >= 2.5
        for idx in series[mask.fillna(False)].index:
            value = float(series.loc[idx])
            direction = "spikes above the recent trend" if z.loc[idx] > 0 else "drops below the recent trend"
            flags.append(
                {
                    "row_index": int(idx),
                    "column": col,
                    "method": "Time-series",
                    "value": round(value, 4),
                    "direction": direction,
                }
            )
    return flags


def _merge_flags(row_hits: dict[int, dict[str, Any]], flags: list[dict[str, Any]]) -> None:
    for flag in flags:
        idx = flag["row_index"]
        if idx not in row_hits:
            row_hits[idx] = {"methods": set(), "columns": {}, "details": []}
        row_hits[idx]["methods"].add(flag["method"])
        row_hits[idx]["columns"][flag["column"]] = flag["direction"]
        row_hits[idx]["details"].append(flag)


def _build_anomaly_rows(df: pd.DataFrame, row_hits: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx in sorted(row_hits.keys()):
        hit = row_hits[idx]
        if not _should_include_row(hit):
            continue
        methods = sorted(hit["methods"])
        columns = hit["columns"]
        severity = "high" if len(methods) >= 2 else "medium"
        explanation = _row_explanation(idx, columns)
        values = {
            col: _safe_value(df.loc[idx, col]) for col in columns.keys() if col in df.columns
        }
        rows.append(
            {
                "row_index": idx,
                "severity": severity,
                "methods": methods,
                "columns": list(columns.keys()),
                "explanation": explanation,
                "values": values,
            }
        )
    rows.sort(key=lambda r: (0 if r["severity"] == "high" else 1, -len(r["methods"])))
    return rows


def _should_include_row(hit: dict[str, Any]) -> bool:
    methods = hit["methods"]
    if len(methods) >= 2:
        return True
    if methods.intersection({"IQR", "Z-score", "Time-series"}):
        return True
    if "Isolation Forest" in methods:
        iso_details = [d for d in hit["details"] if d["method"] == "Isolation Forest"]
        return any(d.get("score", 0) < -0.12 for d in iso_details)
    return False


def _row_explanation(row_index: int, columns: dict[str, str]) -> str:
    if not columns:
        return f"Row {row_index} appears unusual based on multivariate anomaly detection."

    parts = []
    for col, direction in columns.items():
        pretty = _prettify(col)
        if "outside" in direction or "expected" in direction:
            parts.append(f"{pretty} is {direction}")
        else:
            parts.append(f"{pretty} is {direction}")

    if len(parts) == 1:
        detail = parts[0]
    elif len(parts) == 2:
        detail = f"{parts[0]} and {parts[1]}"
    else:
        detail = ", ".join(parts[:-1]) + f", and {parts[-1]}"

    return f"Row {row_index} appears unusual because {detail}."


def _top_anomalous_columns(row_hits: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, dict[str, Any]] = {}
    for hit in row_hits.values():
        for detail in hit["details"]:
            col = detail["column"]
            if col not in counts:
                counts[col] = {"column": col, "anomaly_count": 0, "methods": set()}
            counts[col]["anomaly_count"] += 1
            counts[col]["methods"].add(detail["method"])

    ranked = sorted(counts.values(), key=lambda x: x["anomaly_count"], reverse=True)
    return [
        {
            "column": item["column"],
            "display_name": _prettify(item["column"]),
            "anomaly_count": item["anomaly_count"],
            "methods": sorted(item["methods"]),
        }
        for item in ranked[:10]
    ]


def _severity_score(total_anomalies: int, total_rows: int, methods: list[str]) -> float:
    if total_rows == 0:
        return 0.0
    ratio = min(total_anomalies / total_rows, 1.0)
    method_boost = min(len(methods) * 8, 24)
    return round(min(ratio * 100 + method_boost, 100.0), 2)


def _anomaly_summary(
    total: int, top_columns: list[dict[str, Any]], methods: list[str]
) -> str:
    method_text = ", ".join(methods)
    if not top_columns:
        return f"Found {total} anomalous row(s) using {method_text}."
    top = top_columns[0]["column"]
    return (
        f"Found {total} anomalous row(s). "
        f"Most affected column: '{top}'. Methods used: {method_text}."
    )


def _plain_english_explanation(
    total: int, top_columns: list[dict[str, Any]], methods: list[str]
) -> str:
    if total == 0:
        return "No unusual rows or values were detected."
    method_text = ", ".join(methods)
    if top_columns:
        col = _prettify(top_columns[0]["column"])
        return (
            f"Detected {total} unusual row(s), mainly affecting {col}, "
            f"using {method_text}."
        )
    return f"Detected {total} unusual row(s) using {method_text}."


def _build_chart_data(
    df: pd.DataFrame,
    anomaly_rows: list[dict[str, Any]],
    numeric_cols: list[str],
    datetime_cols: list[str],
) -> dict[str, Any]:
    if not numeric_cols:
        return {}

    anomaly_indices = {row["row_index"] for row in anomaly_rows}
    target_col = numeric_cols[0]

    if datetime_cols:
        date_col = datetime_cols[0]
        work = df[[date_col, target_col]].copy()
        work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
        work[target_col] = pd.to_numeric(work[target_col], errors="coerce")
        work = work.dropna().sort_values(date_col)

        fig = go.Figure()
        normal = work[~work.index.isin(anomaly_indices)]
        anom = work[work.index.isin(anomaly_indices)]
        fig.add_trace(
            go.Scatter(
                x=normal[date_col],
                y=normal[target_col],
                mode="lines+markers",
                name="Normal",
                line=dict(color="#6366f1"),
            )
        )
        if not anom.empty:
            fig.add_trace(
                go.Scatter(
                    x=anom[date_col],
                    y=anom[target_col],
                    mode="markers",
                    name="Anomaly",
                    marker=dict(color="#ef4444", size=10, symbol="x"),
                )
            )
        fig.update_layout(
            title=f"Time-series anomalies in {_prettify(target_col)}",
            xaxis_title=_prettify(date_col),
            yaxis_title=_prettify(target_col),
            margin=dict(l=40, r=20, t=40, b=40),
        )
    else:
        y_col = numeric_cols[1] if len(numeric_cols) > 1 else target_col
        x_series = pd.to_numeric(df[target_col], errors="coerce")
        y_series = pd.to_numeric(df[y_col], errors="coerce")

        fig = go.Figure()
        normal_mask = ~df.index.isin(anomaly_indices)
        fig.add_trace(
            go.Scatter(
                x=x_series[normal_mask],
                y=y_series[normal_mask],
                mode="markers",
                name="Normal",
                marker=dict(color="#6366f1", size=7),
            )
        )
        if anomaly_indices:
            anom_mask = df.index.isin(anomaly_indices)
            fig.add_trace(
                go.Scatter(
                    x=x_series[anom_mask],
                    y=y_series[anom_mask],
                    mode="markers",
                    name="Anomaly",
                    marker=dict(color="#ef4444", size=11, symbol="x"),
                )
            )
        fig.update_layout(
            title="Anomaly scatter plot",
            xaxis_title=_prettify(target_col),
            yaxis_title=_prettify(y_col),
            margin=dict(l=40, r=20, t=40, b=40),
        )

    return {"anomaly_chart": json.loads(pio.to_json(fig))}


def _prettify(name: str) -> str:
    return " ".join(part.capitalize() for part in name.replace("_", " ").split())


def _safe_value(value: Any) -> float | str | None:
    if pd.isna(value):
        return None
    if isinstance(value, (int, float, np.number)):
        return round(float(value), 4)
    return str(value)
