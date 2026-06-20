import pandas as pd
import pytest

from app.services.anomaly_engine import (
    _detect_iqr,
    _detect_isolation_forest,
    _detect_zscore,
    detect_anomalies,
)


def _df_from_dict(data: dict) -> pd.DataFrame:
    return pd.DataFrame(data)


def test_iqr_detects_outlier():
    df = _df_from_dict({"value": [10, 11, 12, 13, 14, 15, 16, 17, 18, 200]})
    flags = _detect_iqr(df, ["value"])
    assert flags
    assert any(flag["row_index"] == 9 for flag in flags)
    assert "IQR" in {flag["method"] for flag in flags}


def test_zscore_detects_outlier():
    df = _df_from_dict({"value": [10, 11, 12, 13, 14, 15, 16, 17, 18, 1000]})
    flags = _detect_zscore(df, ["value"])
    assert flags
    assert any(flag["method"] == "Z-score" for flag in flags)


def test_isolation_forest_detects_multivariate_outlier():
    df = _df_from_dict(
        {
            "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],
            "y": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],
        }
    )
    flags = _detect_isolation_forest(df, ["x", "y"])
    assert flags
    assert any(flag["row_index"] == 10 for flag in flags)


def test_no_anomalies_case():
    df = _df_from_dict({"value": [float(i) for i in range(1, 51)]})
    result = detect_anomalies(df)
    assert result["available"] is True
    assert result["total_anomalies"] == 0


def test_small_dataset_fallback():
    df = _df_from_dict({"value": [1, 2]})
    result = detect_anomalies(df)
    assert result["available"] is False


def test_timeseries_anomalies():
    df = _df_from_dict(
        {
            "date": pd.date_range("2024-01-01", periods=12, freq="MS").astype(str),
            "revenue": [100, 102, 101, 103, 102, 104, 103, 105, 104, 106, 105, 500],
        }
    )
    result = detect_anomalies(df)
    assert result["available"] is True
    assert result["total_anomalies"] >= 1
    assert "Time-series" in result["anomaly_methods_used"] or "IQR" in result["anomaly_methods_used"]
