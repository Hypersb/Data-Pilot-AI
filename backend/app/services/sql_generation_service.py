import re
from typing import Any

import sqlparse

import pandas as pd

from app.services.ingest import infer_column_types


def generate_sql(df: pd.DataFrame, question: str, table_name: str = "dataset") -> dict[str, Any]:
    text = question.lower().strip()
    column_types = infer_column_types(df)
    columns = list(df.columns)
    numeric_cols = [c for c, t in column_types.items() if t == "numeric"]
    categorical_cols = [c for c, t in column_types.items() if t == "categorical"]
    assumptions: list[str] = []
    tables_used = [table_name]
    cols_ref: list[str] = []

    safe_table = re.sub(r"[^\w]", "_", table_name)

    if re.search(r"top\s+\d+|highest|largest|best", text):
        n = _extract_n(text, default=10)
        metric = _pick_col(text, numeric_cols, ["revenue", "sales", "amount", "total"])
        group = _pick_col(text, categorical_cols, ["customer", "product", "region", "category", "name"])
        cols_ref = [group, metric] if group and metric else numeric_cols[:2]
        if group and metric:
            sql = (
                f"SELECT {group},\n"
                f"       SUM({metric}) AS total_{metric}\n"
                f"FROM {safe_table}\n"
                f"GROUP BY {group}\n"
                f"ORDER BY total_{metric} DESC\n"
                f"LIMIT {n};"
            )
            explanation = (
                f"This query ranks each {group} by total {metric}, returning the top {n}. "
                f"SUM aggregates the metric; GROUP BY splits results by {group}."
            )
        else:
            col = metric or (numeric_cols[0] if numeric_cols else columns[0])
            cols_ref = [col]
            sql = f"SELECT *\nFROM {safe_table}\nORDER BY {col} DESC\nLIMIT {n};"
            explanation = f"Returns top {n} rows ordered by {col} descending."
            assumptions.append(f"Assumed sort column: {col}")

    elif re.search(r"average|avg|mean", text):
        metric = _pick_col(text, numeric_cols, ["revenue", "sales", "price", "amount"])
        group = _pick_col(text, categorical_cols, ["region", "category", "segment", "product"])
        if group and metric:
            cols_ref = [group, metric]
            sql = (
                f"SELECT {group},\n"
                f"       AVG({metric}) AS avg_{metric}\n"
                f"FROM {safe_table}\n"
                f"GROUP BY {group};"
            )
            explanation = f"Computes average {metric} for each {group}."
        elif metric:
            cols_ref = [metric]
            sql = f"SELECT AVG({metric}) AS avg_{metric}\nFROM {safe_table};"
            explanation = f"Computes the overall average of {metric}."
        else:
            raise ValueError("No numeric column found for AVG query.")

    elif re.search(r"count|how many", text):
        group = _pick_col(text, categorical_cols, ["customer", "product", "region", "category"])
        if group:
            cols_ref = [group]
            sql = (
                f"SELECT {group},\n"
                f"       COUNT(*) AS row_count\n"
                f"FROM {safe_table}\n"
                f"GROUP BY {group};"
            )
            explanation = f"Counts rows grouped by {group}."
        else:
            sql = f"SELECT COUNT(*) AS total_rows\nFROM {safe_table};"
            explanation = "Counts total rows in the dataset."
            assumptions.append("No grouping column detected; returning total count.")

    elif re.search(r"where|filter|greater|less|above|below", text):
        metric = _pick_col(text, numeric_cols, ["revenue", "sales", "amount", "price"])
        threshold = _extract_number(text)
        if metric and threshold is not None:
            cols_ref = [metric]
            op = ">" if any(w in text for w in ("greater", "above", "more", ">")) else "<"
            sql = f"SELECT *\nFROM {safe_table}\nWHERE {metric} {op} {threshold};"
            explanation = f"Filters rows where {metric} {op} {threshold}."
        else:
            sql = f"SELECT *\nFROM {safe_table}\nLIMIT 100;"
            explanation = "Generic filter — specify column and threshold for a precise WHERE clause."
            assumptions.append("Could not detect filter column/threshold; returning sample rows.")

    else:
        metric = numeric_cols[0] if numeric_cols else columns[0]
        cols_ref = columns[:5]
        sql = f"SELECT {', '.join(cols_ref)}\nFROM {safe_table}\nLIMIT 20;"
        explanation = "General exploration query returning sample columns."
        assumptions.append("Question did not match a known pattern; generated exploratory SELECT.")

    formatted = sqlparse.format(sql, reindent=True, keyword_case="upper")

    return {
        "sql": formatted,
        "explanation": explanation,
        "tables_used": tables_used,
        "columns_referenced": cols_ref,
        "assumptions": assumptions,
    }


def _extract_n(text: str, default: int = 10) -> int:
    m = re.search(r"top\s+(\d+)", text)
    if m:
        return int(m.group(1))
    m = re.search(r"\b(\d+)\b", text)
    return int(m.group(1)) if m else default


def _extract_number(text: str) -> float | None:
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(m.group(1)) if m else None


def _pick_col(text: str, candidates: list[str], keywords: list[str]) -> str | None:
    for kw in keywords:
        if kw in text:
            for c in candidates:
                if kw in c.lower():
                    return c
    for c in candidates:
        if c.lower() in text:
            return c
    return candidates[0] if candidates else None
