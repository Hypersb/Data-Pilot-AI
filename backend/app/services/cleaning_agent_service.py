from __future__ import annotations

import re
from typing import Any, Callable

import pandas as pd

from app.models.cleaning import CleaningAuditEntry
from app.services.health_score_service import compute_health_score
from app.services.ingest import infer_column_types


TransformFn = Callable[[pd.DataFrame, dict[str, Any]], pd.DataFrame]


def apply_cleaning(
    df: pd.DataFrame,
    instruction: str,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    ops = parse_instruction(instruction, list(df.columns))
    work = df.copy()
    audit: list[dict[str, Any]] = []

    for step, (op_name, params) in enumerate(ops, start=1):
        executor = TRANSFORM_REGISTRY.get(op_name)
        if executor is None:
            raise ValueError(f"Unsupported operation: {op_name}")
        rows_before = len(work)
        work = executor(work, params)
        rows_after = len(work)
        audit.append(
            CleaningAuditEntry(
                step=step,
                operation=op_name,
                description=_describe_op(op_name, params),
                rows_before=rows_before,
                rows_after=rows_after,
                columns_affected=params.get("columns", []),
                params=params,
            ).model_dump()
        )

    return work, audit


def parse_instruction(instruction: str, df_columns: list[str] | None = None) -> list[tuple[str, dict[str, Any]]]:
    text = instruction.lower().strip()
    ops: list[tuple[str, dict[str, Any]]] = []

    if re.search(r"remove|drop|delete.*duplicate", text):
        subset = _extract_column(text, df_columns)
        ops.append(("drop_duplicates", {"subset": [subset] if subset else None}))

    if "median" in text and ("fill" in text or "missing" in text):
        col = _extract_column(text, df_columns)
        ops.append(("fillna_median", {"column": col}))

    if "mean" in text and ("fill" in text or "missing" in text):
        col = _extract_column(text, df_columns)
        ops.append(("fillna_mean", {"column": col}))

    if "mode" in text and ("fill" in text or "missing" in text):
        col = _extract_column(text, df_columns)
        ops.append(("fillna_mode", {"column": col}))

    if "datetime" in text or "date" in text:
        col = _extract_column(text, df_columns) or _find_date_column_name(text)
        if col:
            ops.append(("convert_datetime", {"column": col}))

    if "outlier" in text and ("remove" in text or "drop" in text):
        col = _extract_column(text, df_columns)
        ops.append(("remove_outliers", {"column": col}))

    if re.search(r"drop|remove.*column", text) and "duplicate" not in text:
        col = _extract_column(text, df_columns)
        if col:
            ops.append(("drop_column", {"column": col}))

    if "numeric" in text or "convert" in text and "number" in text:
        col = _extract_column(text, df_columns)
        if col:
            ops.append(("cast_numeric", {"column": col}))

    if not ops:
        raise ValueError(
            "Could not parse cleaning instruction. Try: 'Remove duplicate customers', "
            "'Fill missing revenue with median', or 'Convert order_date to datetime'."
        )

    return ops


def _extract_column(text: str, df_columns: list[str] | None = None) -> str | None:
    quoted = re.findall(r"['\"]([\w\s]+)['\"]", text)
    if quoted:
        name = quoted[0].strip().replace(" ", "_")
        return _match_column(name, df_columns)
    words = re.findall(r"\b([a-z][a-z0-9_]*)\b", text)
    skip = {"remove", "drop", "delete", "fill", "missing", "with", "median", "mean",
            "mode", "convert", "to", "datetime", "date", "duplicate", "duplicates",
            "column", "outlier", "outliers", "the", "all", "and", "numeric", "number",
            "customers", "customer", "rows", "values"}
    for w in reversed(words):
        if w not in skip and len(w) > 2:
            matched = _match_column(w, df_columns)
            if matched:
                return matched
    if df_columns:
        for col in df_columns:
            if col.lower() in text:
                return col
    return None


def _match_column(name: str, df_columns: list[str] | None) -> str | None:
    if not df_columns:
        return name
    if name in df_columns:
        return name
    for col in df_columns:
        if col.lower() == name.lower():
            return col
        if name.rstrip("s") in col.lower() or col.lower() in name:
            return col
    return None


def _find_date_column_name(text: str) -> str | None:
    m = re.search(r"(\w*date\w*|\w*time\w*)", text)
    return m.group(1) if m else None


def _describe_op(op_name: str, params: dict[str, Any]) -> str:
    col = params.get("column") or params.get("subset")
    if op_name == "drop_duplicates":
        return "Removed duplicate rows" + (f" on {col}" if col else "")
    if op_name.startswith("fillna"):
        strategy = op_name.replace("fillna_", "")
        return f"Filled missing values in '{col}' with {strategy}"
    if op_name == "convert_datetime":
        return f"Converted '{col}' to datetime"
    if op_name == "remove_outliers":
        return f"Removed outliers from '{col or 'numeric columns'}' using IQR"
    if op_name == "drop_column":
        return f"Dropped column '{col}'"
    if op_name == "cast_numeric":
        return f"Cast '{col}' to numeric"
    return op_name


def _op_drop_duplicates(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    subset = params.get("subset")
    if subset and subset[0] and subset[0] in df.columns:
        return df.drop_duplicates(subset=subset)
    return df.drop_duplicates()


def _op_fillna_median(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    col = _resolve_column(df, params.get("column"))
    work = df.copy()
    work[col] = pd.to_numeric(work[col], errors="coerce")
    work[col] = work[col].fillna(work[col].median())
    return work


def _op_fillna_mean(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    col = _resolve_column(df, params.get("column"))
    work = df.copy()
    work[col] = pd.to_numeric(work[col], errors="coerce")
    work[col] = work[col].fillna(work[col].mean())
    return work


def _op_fillna_mode(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    col = _resolve_column(df, params.get("column"))
    work = df.copy()
    mode = work[col].mode()
    if len(mode):
        work[col] = work[col].fillna(mode.iloc[0])
    return work


def _op_convert_datetime(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    col = _resolve_column(df, params.get("column"))
    work = df.copy()
    work[col] = pd.to_datetime(work[col], errors="coerce")
    return work


def _op_remove_outliers(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    col = params.get("column")
    work = df.copy()
    cols = [col] if col and col in work.columns else [
        c for c, t in infer_column_types(work).items() if t == "numeric"
    ][:3]
    mask = pd.Series([True] * len(work), index=work.index)
    for c in cols:
        series = pd.to_numeric(work[c], errors="coerce")
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        mask &= (series >= q1 - 1.5 * iqr) & (series <= q3 + 1.5 * iqr) | series.isna()
    return work[mask]


def _op_drop_column(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    col = _resolve_column(df, params.get("column"))
    return df.drop(columns=[col])


def _op_cast_numeric(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    col = _resolve_column(df, params.get("column"))
    work = df.copy()
    work[col] = pd.to_numeric(work[col], errors="coerce")
    return work


def _resolve_column(df: pd.DataFrame, requested: str | None) -> str:
    if requested and requested in df.columns:
        return requested
    for col in df.columns:
        if requested and requested.lower() in col.lower():
            return col
    numeric = [c for c, t in infer_column_types(df).items() if t == "numeric"]
    if numeric:
        return numeric[0]
    raise ValueError(f"Column '{requested}' not found.")


TRANSFORM_REGISTRY: dict[str, TransformFn] = {
    "drop_duplicates": _op_drop_duplicates,
    "fillna_median": _op_fillna_median,
    "fillna_mean": _op_fillna_mean,
    "fillna_mode": _op_fillna_mode,
    "convert_datetime": _op_convert_datetime,
    "remove_outliers": _op_remove_outliers,
    "drop_column": _op_drop_column,
    "cast_numeric": _op_cast_numeric,
}
