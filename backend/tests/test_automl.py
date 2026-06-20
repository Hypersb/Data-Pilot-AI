import pandas as pd
import pytest

from app.services.automl_engine import detect_task, run_automl
from app.services.ingest import parse_upload


FORECAST_CSV = b"""date,revenue,units
2024-01-01,100,10
2024-02-01,110,11
2024-03-01,120,12
2024-04-01,130,13
2024-05-01,140,14
2024-06-01,150,15
2024-07-01,160,16
2024-08-01,170,17
2024-09-01,180,18
2024-10-01,190,19
2024-11-01,200,20
2024-12-01,210,21
"""

REGRESSION_CSV = b"""feature_a,feature_b,revenue
1.0,2.0,10.5
2.0,3.0,15.2
3.0,4.0,18.1
4.0,5.0,22.0
5.0,6.0,25.5
6.0,7.0,28.3
7.0,8.0,31.0
8.0,9.0,34.2
9.0,10.0,37.5
10.0,11.0,40.0
11.0,12.0,43.1
12.0,13.0,46.0
"""

CLASSIFICATION_CSV = b"""age,income,region,churn
25,50000,North,0
30,60000,South,0
35,70000,East,1
40,80000,West,0
45,90000,North,1
50,100000,South,0
28,55000,East,0
33,65000,West,1
38,75000,North,0
42,85000,South,1
"""


@pytest.fixture
def forecast_df():
    return parse_upload(FORECAST_CSV, "forecast.csv")


@pytest.fixture
def regression_df():
    return parse_upload(REGRESSION_CSV, "regression.csv")


@pytest.fixture
def classification_df():
    return parse_upload(CLASSIFICATION_CSV, "classification.csv")


def test_detect_forecasting_task(forecast_df):
    detection = detect_task(forecast_df, target_column="revenue", date_column="date")
    assert detection.task_type == "forecasting"
    assert detection.target_column == "revenue"
    assert detection.date_column == "date"


def test_detect_regression_task(regression_df):
    detection = detect_task(regression_df, target_column="revenue")
    assert detection.task_type == "regression"
    assert "feature_a" in detection.feature_columns


def test_detect_classification_task(classification_df):
    detection = detect_task(classification_df, target_column="churn")
    assert detection.task_type == "classification"
    assert detection.target_column == "churn"


def test_run_automl_forecasting(forecast_df):
    result = run_automl(forecast_df, target_column="revenue", date_column="date")
    assert result["task_type"] == "forecasting"
    assert result["best_model"]["model_name"]
    assert len(result["leaderboard"]) >= 1
    assert result["leaderboard"][0]["is_best"] is True
    for entry in result["leaderboard"]:
        assert "mape" in entry["metrics"]
        assert "rmse" in entry["metrics"]


def test_run_automl_regression(regression_df):
    result = run_automl(regression_df, target_column="revenue")
    assert result["task_type"] == "regression"
    assert len(result["leaderboard"]) >= 2
    best = result["best_model"]
    assert "r2" in best["metrics"]
    assert "rmse" in best["metrics"]
    assert "mae" in best["metrics"]
    assert any(entry["is_best"] for entry in result["leaderboard"])


def test_run_automl_classification(classification_df):
    result = run_automl(classification_df, target_column="churn")
    assert result["task_type"] == "classification"
    assert len(result["leaderboard"]) >= 2
    best = result["best_model"]
    assert "accuracy" in best["metrics"]
    assert "precision" in best["metrics"]
    assert "recall" in best["metrics"]
    assert "f1" in best["metrics"]


def test_leaderboard_ranking_regression(regression_df):
    result = run_automl(regression_df, target_column="revenue")
    ranks = [entry["rank"] for entry in result["leaderboard"]]
    assert ranks == sorted(ranks)
    assert result["leaderboard"][0]["model_name"] == result["best_model"]["model_name"]


def test_automl_insufficient_data():
    df = pd.DataFrame({"x": [1], "y": [2]})
    with pytest.raises(ValueError):
        run_automl(df, target_column="y")
