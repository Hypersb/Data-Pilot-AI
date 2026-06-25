import io
from typing import Any

import pandas as pd


ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def validate_extension(filename: str) -> str:
    lower = filename.lower()
    for ext in ALLOWED_EXTENSIONS:
        if lower.endswith(ext):
            return ext
    raise ValueError("Unsupported file type. Please upload CSV or Excel (.xlsx, .xls).")


def parse_upload(content: bytes, filename: str) -> pd.DataFrame:
    ext = validate_extension(filename)
    buffer = io.BytesIO(content)

    if ext == ".csv":
        df = pd.read_csv(buffer)
    else:
        df = pd.read_excel(buffer, engine="openpyxl")

    if df.empty:
        raise ValueError("Uploaded file contains no data.")

    df.columns = [str(c).strip() for c in df.columns]
    return df


def dataframe_preview(df: pd.DataFrame, rows: int = 5) -> list[dict[str, Any]]:
    preview = df.head(rows).copy()
    for col in preview.columns:
        if pd.api.types.is_datetime64_any_dtype(preview[col]):
            preview[col] = preview[col].dt.strftime("%Y-%m-%d")
    preview = preview.where(pd.notnull(preview), None)
    return preview.to_dict(orient="records")


_ID_LIKE_COLUMNS = {"#", "id", "index", "row", "row_id", "uuid", "pk", "key"}


def infer_column_types(df: pd.DataFrame) -> dict[str, str]:
    result: dict[str, str] = {}
    for col in df.columns:
        series = df[col]
        col_key = str(col).strip().lower()
        if col_key in _ID_LIKE_COLUMNS:
            coerced = pd.to_numeric(series, errors="coerce")
            if coerced.notna().sum() >= max(1, len(series) * 0.8):
                result[col] = "numeric"
                continue
        if pd.api.types.is_bool_dtype(series):
            result[col] = "categorical"
            continue
        if pd.api.types.is_numeric_dtype(series):
            result[col] = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(series):
            result[col] = "datetime"
        else:
            parsed = pd.to_datetime(series, errors="coerce", utc=False)
            if parsed.notna().sum() >= len(series) * 0.8:
                result[col] = "datetime"
            elif series.nunique(dropna=True) <= min(50, max(1, len(series) // 2)):
                result[col] = "categorical"
            else:
                result[col] = "text"
    return result
