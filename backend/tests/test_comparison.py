import io

import pandas as pd
import pytest

from app.services.comparison_service import compare_datasets, compare_periods

SAMPLE_CSV = b"""date,region,revenue
2024-01-01,North,100
2024-02-01,North,110
2024-03-01,North,120
2024-04-01,South,90
2024-05-01,South,95
2024-06-01,South,100
"""


def test_compare_periods():
    df = pd.read_csv(io.BytesIO(SAMPLE_CSV))
    result = compare_periods(df, metric_column="revenue", date_column="date", period="mom")
    assert result["metric_column"] == "revenue"
    assert len(result["changes"]) >= 1


def test_compare_datasets():
    df_a = pd.read_csv(io.BytesIO(SAMPLE_CSV))
    df_b = df_a.copy()
    df_b["revenue"] = df_b["revenue"] * 1.1
    result = compare_datasets(df_a, df_b, "a", "b")
    assert result["session_id_a"] == "a"
    assert len(result["metric_comparisons"]) >= 1
