import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.forecast_engine import (
    _backtest_arima,
    _backtest_prophet,
    _backtest_xgb_lags,
    _prepare_series,
    _rank_leaderboard,
    run_forecast_leaderboard,
)
from app.services.ingest import parse_upload

client = TestClient(app)

FORECAST_CSV = b"""date,revenue
2024-01-01,100
2024-02-01,110
2024-03-01,120
2024-04-01,130
2024-05-01,140
2024-06-01,150
2024-07-01,160
2024-08-01,170
2024-09-01,180
2024-10-01,190
2024-11-01,200
2024-12-01,210
"""


@pytest.fixture
def forecast_df():
    return parse_upload(FORECAST_CSV, "forecast.csv")


@pytest.fixture
def series_df(forecast_df):
    return _prepare_series(forecast_df, "date", "revenue")


def test_arima_backtest(series_df):
    y = series_df["revenue"].to_numpy(dtype=float)
    result = _backtest_arima(series_df, "date", "revenue", y)
    assert result is not None
    actuals, preds = result
    assert len(actuals) == len(preds)
    assert len(actuals) >= 1


def test_prophet_backtest(series_df):
    y = series_df["revenue"].to_numpy(dtype=float)
    result = _backtest_prophet(series_df, "date", "revenue", y)
    assert result is not None
    actuals, preds = result
    assert len(actuals) == len(preds)


def test_xgb_backtest(series_df):
    y = series_df["revenue"].to_numpy(dtype=float)
    result = _backtest_xgb_lags(series_df, "date", "revenue", y)
    assert result is not None
    actuals, preds = result
    assert len(actuals) == len(preds)


def test_leaderboard_ranking():
    entries = [
        {"model_name": "ARIMA", "metrics": {"mape": 12.0, "rmse": 5.0, "mae": 4.0}, "status": "success"},
        {"model_name": "Prophet", "metrics": {"mape": 6.2, "rmse": 3.0, "mae": 2.5}, "status": "success"},
        {"model_name": "XGBoost Regressor", "metrics": {"mape": 8.0, "rmse": 4.0, "mae": 3.0}, "status": "success"},
    ]
    ranked = _rank_leaderboard(entries)
    assert ranked[0]["model_name"] == "Prophet"
    assert ranked[0]["rank"] == 1
    assert ranked[0]["is_best"] is True
    assert ranked[1]["rank"] == 2
    assert ranked[2]["rank"] == 3


def test_run_forecast_leaderboard(forecast_df):
    result = run_forecast_leaderboard(forecast_df, forecast_horizon=3)
    assert result["available"] is True
    assert result["target_column"] == "revenue"
    assert result["date_column"] == "date"
    assert len(result["leaderboard"]) >= 1
    assert result["best_model"]["is_best"] is True
    assert "MAPE" in result["explanation"] or "mape" in result["explanation"].lower()
    assert len(result["forecast"]) == 3
    assert "forecast_chart" in result["chart_data"]
    for point in result["forecast"]:
        assert "date" in point
        assert "value" in point


def test_invalid_date_column(forecast_df):
    with pytest.raises(ValueError, match="date column"):
        run_forecast_leaderboard(forecast_df, date_column="not_a_column")


def test_missing_target_column(forecast_df):
    with pytest.raises(ValueError, match="target column"):
        run_forecast_leaderboard(forecast_df, target_column="missing_col")


def test_small_dataset_raises():
    tiny = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=5, freq="MS"), "revenue": [1, 2, 3, 4, 5]})
    with pytest.raises(ValueError, match="Not enough data"):
        run_forecast_leaderboard(tiny)


def test_prepare_series_drops_missing_dates():
    df = pd.DataFrame(
        {
            "date": ["2024-01-01", None, "2024-03-01", "2024-04-01", "2024-05-01", "2024-06-01", "2024-07-01", "2024-08-01"],
            "revenue": [10, 20, 30, 40, 50, 60, 70, 80],
        }
    )
    series = _prepare_series(df, "date", "revenue")
    assert len(series) == 7


def test_forecast_api_get():
    upload = client.post(
        "/api/upload",
        files={"file": ("forecast.csv", FORECAST_CSV, "text/csv")},
    )
    assert upload.status_code == 200
    session_id = upload.json()["session_id"]

    resp = client.get(
        f"/api/sessions/{session_id}/forecast",
        params={"target_column": "revenue", "date_column": "date", "forecast_horizon": 4},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["available"] is True
    assert data["forecast_horizon"] == 4
    assert len(data["leaderboard"]) >= 1
    assert data["best_model"]["model_name"]
    assert data["explanation"]
    assert len(data["forecast"]) == 4
    assert "forecast_chart" in data["chart_data"]


def test_forecast_api_invalid_column():
    upload = client.post(
        "/api/upload",
        files={"file": ("forecast.csv", FORECAST_CSV, "text/csv")},
    )
    session_id = upload.json()["session_id"]

    resp = client.get(
        f"/api/sessions/{session_id}/forecast",
        params={"target_column": "revenue", "date_column": "bad_date"},
    )
    assert resp.status_code == 400
