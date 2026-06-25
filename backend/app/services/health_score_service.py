from typing import Any

import numpy as np
import pandas as pd

from app.services.ingest import infer_column_types
from app.services.profiler import profile_dataframe
from app.utils.datetime_utils import has_future_dates, parse_datetime_series
from app.utils.outlier_utils import aggregate_outlier_rate, iqr_outlier_rate
from app.utils.scoring import score_from_ratio, weighted_score


def compute_health_score(df: pd.DataFrame) -> dict[str, Any]:
    profile = profile_dataframe(df)
    column_types = infer_column_types(df)
    numeric_cols = [
        c
        for c, t in column_types.items()
        if t == "numeric" and not pd.api.types.is_bool_dtype(df[c])
    ]
    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols if total_cols else 0

    missing_cells = int(df.isna().sum().sum())
    completeness = score_from_ratio(total_cells - missing_cells, total_cells) if total_cells else 100.0

    consistency_scores: list[float] = []
    for col in df.columns:
        col_type = column_types[col]
        series = df[col].dropna()
        if len(series) == 0:
            continue
        if col_type == "numeric":
            coerced = pd.to_numeric(series, errors="coerce")
            consistency_scores.append(score_from_ratio(coerced.notna().sum(), len(series)))
        elif col_type == "datetime":
            parsed = pd.to_datetime(series, errors="coerce")
            consistency_scores.append(score_from_ratio(parsed.notna().sum(), len(series)))
        else:
            consistency_scores.append(100.0)
    consistency = round(sum(consistency_scores) / len(consistency_scores), 2) if consistency_scores else 100.0

    duplicate_rows = int(df.duplicated().sum())
    uniqueness = score_from_ratio(total_rows - duplicate_rows, total_rows) if total_rows else 100.0

    null_pcts = [info["null_pct"] for info in profile["columns_info"]]
    avg_null = sum(null_pcts) / len(null_pcts) if null_pcts else 0.0
    missing_value_score = round(max(0.0, 100.0 - avg_null), 2)
    duplicate_score = uniqueness
    outlier_score = aggregate_outlier_rate(df, numeric_cols)

    validity_issues = _validity_checks(df, column_types)
    validity = round(max(0.0, 100.0 - len(validity_issues) * 8), 2)

    sub_scores = {
        "completeness": completeness,
        "consistency": consistency,
        "uniqueness": uniqueness,
        "validity": validity,
        "missing_value_score": missing_value_score,
        "duplicate_score": duplicate_score,
        "outlier_score": outlier_score,
    }
    weights = {
        "completeness": 1.5,
        "consistency": 1.0,
        "uniqueness": 1.2,
        "validity": 1.0,
        "missing_value_score": 1.0,
        "duplicate_score": 0.8,
        "outlier_score": 0.5,
    }
    overall = weighted_score(sub_scores, weights)

    issues = _build_issues(df, profile, column_types, numeric_cols, validity_issues)
    recommended_fixes = list(dict.fromkeys(i["recommended_fix"] for i in issues if i.get("recommended_fix")))

    return {
        "overall_score": overall,
        "sub_scores": sub_scores,
        "issues": issues[:20],
        "recommended_fixes": recommended_fixes[:10],
        "rows": total_rows,
        "columns": total_cols,
    }


def _validity_checks(df: pd.DataFrame, column_types: dict[str, str]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for col, col_type in column_types.items():
        if col_type != "numeric":
            continue
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(series) == 0:
            continue
        col_lower = col.lower()
        if any(k in col_lower for k in ("revenue", "price", "amount", "cost", "sales")):
            negatives = int((series < 0).sum())
            if negatives > 0:
                issues.append(
                    {
                        "severity": "high",
                        "column": col,
                        "description": f"{negatives} negative values in '{col}'.",
                        "recommended_fix": "filter_rows",
                    }
                )
    for col, col_type in column_types.items():
        if col_type == "datetime" and has_future_dates(df[col]):
            issues.append(
                {
                    "severity": "medium",
                    "column": col,
                    "description": f"Future dates detected in '{col}'.",
                    "recommended_fix": "filter_rows",
                }
            )
    return issues


def _build_issues(
    df: pd.DataFrame,
    profile: dict[str, Any],
    column_types: dict[str, str],
    numeric_cols: list[str],
    validity_issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = list(validity_issues)

    if profile["duplicate_rows"] > 0:
        issues.append(
            {
                "severity": "high" if profile["duplicate_rows"] > len(df) * 0.05 else "medium",
                "column": None,
                "description": f"{profile['duplicate_rows']} duplicate rows detected.",
                "recommended_fix": "drop_duplicates",
            }
        )

    for info in profile["columns_info"]:
        if info["null_pct"] > 20:
            fix = "fillna_median" if info["dtype"] == "numeric" else "fillna_mode"
            issues.append(
                {
                    "severity": "high" if info["null_pct"] > 50 else "medium",
                    "column": info["name"],
                    "description": f"Column '{info['name']}' has {info['null_pct']}% missing values.",
                    "recommended_fix": fix,
                }
            )
        if info["unique_count"] == 1 and info["null_count"] < profile["rows"]:
            issues.append(
                {
                    "severity": "low",
                    "column": info["name"],
                    "description": f"Column '{info['name']}' is constant.",
                    "recommended_fix": "drop_column",
                }
            )

    for col in numeric_cols[:5]:
        rate = iqr_outlier_rate(df[col])
        if rate > 5:
            issues.append(
                {
                    "severity": "medium" if rate < 10 else "high",
                    "column": col,
                    "description": f"{rate}% outlier rate in '{col}' (IQR method).",
                    "recommended_fix": "remove_outliers",
                }
            )

    for col, col_type in column_types.items():
        if col_type == "datetime":
            parsed = parse_datetime_series(df[col])
            fail_rate = parsed.isna().sum() / max(len(df), 1) * 100
            if fail_rate > 10:
                issues.append(
                    {
                        "severity": "medium",
                        "column": col,
                        "description": f"Column '{col}' has {fail_rate:.1f}% unparseable dates.",
                        "recommended_fix": "convert_datetime",
                    }
                )

    severity_order = {"high": 0, "medium": 1, "low": 2}
    issues.sort(key=lambda x: severity_order.get(x["severity"], 3))
    return issues
