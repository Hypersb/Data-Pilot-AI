import io

import pandas as pd
import pytest

from app.services.root_cause_service import analyze_root_cause

SAMPLE_CSV = b"""date,region,product,revenue
2024-01-01,North,A,100
2024-02-01,North,A,110
2024-03-01,North,A,120
2024-04-01,South,B,90
2024-05-01,South,B,95
2024-06-01,South,B,100
2024-07-01,North,A,130
2024-08-01,North,A,140
"""


@pytest.fixture
def df():
    return pd.read_csv(io.BytesIO(SAMPLE_CSV))


def test_root_cause_contributors(df):
    result = analyze_root_cause(df, "revenue", period_column="date")
    assert "contributors" in result
    assert len(result["contributors"]) > 0
    top = result["contributors"][0]
    assert "contribution_pct" in top
    assert "delta" in top


def test_root_cause_metric_change(df):
    result = analyze_root_cause(df, "revenue")
    assert "metric_change_pct" in result
    assert result["baseline_total"] != result["comparison_total"] or result["total_delta"] == 0
