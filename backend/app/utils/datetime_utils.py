from typing import Any

import pandas as pd


def parse_datetime_column(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_datetime(df[col], errors="coerce")


def resample_period(
    df: pd.DataFrame,
    date_col: str,
    metric_col: str,
    freq: str = "M",
) -> pd.DataFrame:
    """Resample metric by period. freq: M=month, Q=quarter, Y=year."""
    work = df[[date_col, metric_col]].copy()
    work[date_col] = parse_datetime_column(work, date_col)
    work = work.dropna(subset=[date_col])
    work[metric_col] = pd.to_numeric(work[metric_col], errors="coerce")
    work = work.dropna(subset=[metric_col])
    work = work.set_index(date_col)
    resampled = work[metric_col].resample(freq).sum()
    return resampled.reset_index()


def period_over_period_change(
    series: pd.Series,
) -> list[dict[str, Any]]:
    """Compute period-over-period changes from a time-indexed series."""
    changes: list[dict[str, Any]] = []
    values = series.values
    index = series.index
    for i in range(1, len(values)):
        prev, curr = values[i - 1], values[i]
        if prev == 0:
            pct = 100.0 if curr != 0 else 0.0
        else:
            pct = round((curr - prev) / abs(prev) * 100, 2)
        changes.append(
            {
                "period": str(index[i]),
                "previous_period": str(index[i - 1]),
                "value": round(float(curr), 4),
                "previous_value": round(float(prev), 4),
                "change_pct": pct,
                "delta": round(float(curr - prev), 4),
            }
        )
    return changes


def split_halves(df: pd.DataFrame, date_col: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = df.copy()
    work[date_col] = parse_datetime_column(work, date_col)
    work = work.dropna(subset=[date_col]).sort_values(date_col)
    mid = len(work) // 2
    return work.iloc[:mid], work.iloc[mid:]
