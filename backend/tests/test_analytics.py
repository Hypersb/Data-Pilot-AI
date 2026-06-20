import pandas as pd
import pytest

from app.services.forecast_engine import run_forecast
from app.services.ingest import parse_upload
from app.services.insight_engine import generate_insights
from app.services.profiler import profile_dataframe
from app.services.viz_engine import generate_charts


SAMPLE_CSV = b"""date,region,product,revenue
2024-01-01,North,A,100
2024-02-01,North,A,110
2024-03-01,North,A,120
2024-04-01,North,A,130
2024-05-01,North,A,140
2024-06-01,South,B,90
2024-07-01,South,B,95
2024-08-01,South,B,100
"""


@pytest.fixture
def sample_df():
    return parse_upload(SAMPLE_CSV, "test.csv")


def test_parse_upload(sample_df):
    assert len(sample_df) == 8
    assert "revenue" in sample_df.columns


def test_profile(sample_df):
    profile = profile_dataframe(sample_df)
    assert profile["rows"] == 8
    assert profile["quality_score"] >= 0


def test_insights(sample_df):
    insights = generate_insights(sample_df)
    assert len(insights) >= 1


def test_charts(sample_df):
    charts = generate_charts(sample_df)
    assert len(charts) >= 1


def test_forecast(sample_df):
    result = run_forecast(sample_df, periods=2)
    assert result["model_used"]
    assert len(result["forecast"]) == 2
