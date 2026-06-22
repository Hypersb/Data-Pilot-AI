from typing import Any

import pandas as pd

from app.utils.datetime_utils import parse_datetime_column, split_halves
from app.utils.schema_utils import pick_dimension_columns, pick_metric_column


def analyze_root_cause(
    df: pd.DataFrame,
    metric_column: str,
    dimension_columns: list[str] | None = None,
    period_column: str | None = None,
) -> dict[str, Any]:
    if metric_column not in df.columns:
        raise ValueError(f"Metric column '{metric_column}' not found.")

    work = df.copy()
    work[metric_column] = pd.to_numeric(work[metric_column], errors="coerce")
    work = work.dropna(subset=[metric_column])

    dims = pick_dimension_columns(work, dimension_columns)
    if not dims:
        raise ValueError("No dimension columns available for root cause analysis.")

    if period_column and period_column in work.columns:
        baseline_df, comparison_df = split_halves(work, period_column)
    else:
        mid = len(work) // 2
        baseline_df = work.iloc[:mid]
        comparison_df = work.iloc[mid:]

    baseline_total = float(baseline_df[metric_column].sum())
    comparison_total = float(comparison_df[metric_column].sum())
    total_delta = comparison_total - baseline_total

    if baseline_total != 0:
        metric_change_pct = round(total_delta / abs(baseline_total) * 100, 2)
    else:
        metric_change_pct = 100.0 if comparison_total != 0 else 0.0

    contributors: list[dict[str, Any]] = []
    for dim in dims:
        base_grp = baseline_df.groupby(dim, dropna=False)[metric_column].sum()
        comp_grp = comparison_df.groupby(dim, dropna=False)[metric_column].sum()
        all_values = set(str(x) for x in base_grp.index) | set(str(x) for x in comp_grp.index)
        for val in all_values:
            b_val = _safe_group_val(base_grp, val)
            c_val = _safe_group_val(comp_grp, val)
            delta = c_val - b_val
            if total_delta != 0:
                contribution_pct = round(delta / total_delta * 100, 2)
            else:
                contribution_pct = 0.0
            contributors.append(
                {
                    "dimension": dim,
                    "value": str(val),
                    "baseline_value": round(b_val, 4),
                    "comparison_value": round(c_val, 4),
                    "delta": round(delta, 4),
                    "contribution_pct": contribution_pct,
                }
            )

    contributors.sort(key=lambda x: abs(x["contribution_pct"]), reverse=True)
    top = contributors[:15]

    chart_data = {
        "type": "bar",
        "labels": [f"{c['dimension']}={c['value']}" for c in top[:10]],
        "values": [c["contribution_pct"] for c in top[:10]],
        "title": f"Root cause contributors for {metric_column}",
    }

    return {
        "metric_column": metric_column,
        "metric_change_pct": metric_change_pct,
        "total_delta": round(total_delta, 4),
        "baseline_total": round(baseline_total, 4),
        "comparison_total": round(comparison_total, 4),
        "contributors": top,
        "chart_data": chart_data,
    }


def _safe_group_val(grouped: pd.Series, val: str) -> float:
    for idx in grouped.index:
        if str(idx) == str(val):
            return float(grouped.loc[idx])
    return 0.0
