from typing import Any, Literal

import pandas as pd

from app.utils.datetime_utils import period_over_period_change, resample_period
from app.utils.schema_utils import align_schemas, pick_date_column, pick_metric_column


def compare_periods(
    df: pd.DataFrame,
    metric_column: str | None = None,
    date_column: str | None = None,
    period: Literal["mom", "qoq", "yoy"] = "mom",
) -> dict[str, Any]:
    metric = pick_metric_column(df, metric_column)
    if not metric:
        raise ValueError("No numeric metric column found.")
    date_col = pick_date_column(df, date_column)
    if not date_col:
        raise ValueError("No date column found for period comparison.")

    freq_map = {"mom": "ME", "qoq": "QE", "yoy": "YE"}
    freq = freq_map.get(period, "ME")
    resampled = resample_period(df, date_col, metric, freq)
    if len(resampled) < 2:
        raise ValueError("Insufficient periods for comparison.")

    resampled = resampled.set_index(date_col)
    changes = period_over_period_change(resampled[metric])

    emerging: list[str] = []
    for ch in changes[-3:]:
        if ch["change_pct"] > 10:
            emerging.append(f"Growth of {ch['change_pct']:.1f}% in period {ch['period']}.")
        elif ch["change_pct"] < -10:
            emerging.append(f"Decline of {ch['change_pct']:.1f}% in period {ch['period']}.")

    latest = changes[-1] if changes else {}
    summary = (
        f"{metric} {period.upper()} comparison: latest period changed "
        f"{latest.get('change_pct', 0):.1f}% ({latest.get('delta', 0):+,.2f})."
        if latest
        else f"No period changes computed for {metric}."
    )

    return {
        "metric_column": metric,
        "date_column": date_col,
        "period_type": period,
        "changes": changes,
        "summary": summary,
        "emerging_trends": emerging,
    }


def compare_datasets(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    session_id_a: str,
    session_id_b: str,
    metric_columns: list[str] | None = None,
) -> dict[str, Any]:
    alignment = align_schemas(df_a, df_b)
    common = alignment["common_columns"]

    if metric_columns:
        metrics = [c for c in metric_columns if c in common]
    else:
        metrics = [
            c for c in common
            if pd.api.types.is_numeric_dtype(df_a[c]) or pd.api.types.is_numeric_dtype(df_b[c])
        ][:5]

    metric_comparisons: list[dict[str, Any]] = []
    for col in metrics:
        a_vals = pd.to_numeric(df_a[col], errors="coerce").dropna()
        b_vals = pd.to_numeric(df_b[col], errors="coerce").dropna()
        a_sum = float(a_vals.sum()) if len(a_vals) else 0.0
        b_sum = float(b_vals.sum()) if len(b_vals) else 0.0
        delta = b_sum - a_sum
        pct = round(delta / abs(a_sum) * 100, 2) if a_sum != 0 else (100.0 if b_sum else 0.0)
        metric_comparisons.append(
            {
                "column": col,
                "dataset_a_total": round(a_sum, 4),
                "dataset_b_total": round(b_sum, 4),
                "delta": round(delta, 4),
                "change_pct": pct,
            }
        )

    category_shifts: list[dict[str, Any]] = []
    for col in common:
        if df_a[col].nunique() > 50:
            continue
        if not (df_a[col].dtype == object or str(df_a[col].dtype) == "category"):
            continue
        freq_a = df_a[col].value_counts(normalize=True).head(5)
        freq_b = df_b[col].value_counts(normalize=True).head(5)
        for val in set(freq_a.index) | set(freq_b.index):
            a_pct = float(freq_a.get(val, 0) * 100)
            b_pct = float(freq_b.get(val, 0) * 100)
            shift = round(b_pct - a_pct, 2)
            if abs(shift) > 5:
                category_shifts.append(
                    {"column": col, "value": str(val), "shift_pct": shift}
                )

    row_delta = len(df_b) - len(df_a)
    summary = (
        f"Dataset B has {len(df_b)} rows vs {len(df_a)} in Dataset A ({row_delta:+d} rows). "
        f"{len(common)} shared columns, {len(alignment['only_in_a'])} only in A, "
        f"{len(alignment['only_in_b'])} only in B."
    )

    return {
        "session_id_a": session_id_a,
        "session_id_b": session_id_b,
        "schema_alignment": alignment,
        "metric_comparisons": metric_comparisons,
        "summary": summary,
        "category_shifts": category_shifts[:10],
    }
