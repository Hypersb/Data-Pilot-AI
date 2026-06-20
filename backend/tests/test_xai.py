import numpy as np
import pytest
from sklearn.linear_model import LinearRegression

from app.services.automl_engine import create_model, fit_best_tabular_model, run_automl
from app.services.ingest import parse_upload
from app.services.xai_engine import (
    FALLBACK_MESSAGE,
    _compute_shap_values,
    _is_linear_model,
    _is_tree_model,
    run_xai_explanation,
)


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
13.0,14.0,49.0
14.0,15.0,52.0
15.0,16.0,55.0
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
47,95000,East,0
31,62000,West,1
36,72000,North,0
41,82000,South,1
"""

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
def regression_df():
    return parse_upload(REGRESSION_CSV, "regression.csv")


@pytest.fixture
def classification_df():
    return parse_upload(CLASSIFICATION_CSV, "classification.csv")


@pytest.fixture
def forecast_df():
    return parse_upload(FORECAST_CSV, "forecast.csv")


def test_xai_returns_top_features(regression_df):
    result = run_xai_explanation(regression_df, target_column="revenue")
    assert result["available"] is True
    assert len(result["top_features"]) <= 10
    assert result["top_features"][0]["rank"] == 1
    assert result["global_explanation"].startswith("The model predicts")


def test_xai_tree_model(regression_df):
    result = run_xai_explanation(regression_df, target_column="revenue")
    assert result["available"] is True
    assert _is_tree_model(create_model("regression", "Random Forest Regressor"))


def test_xai_linear_model(regression_df):
    model, X, _, feature_names, _ = fit_best_tabular_model(
        regression_df, "regression", "revenue", ["feature_a", "feature_b"], "Linear Regression"
    )
    assert _is_linear_model(model)
    values = _compute_shap_values(model, X[:5], "regression")
    assert values.shape[0] == 5
    assert values.shape[1] == len(feature_names)


def test_xai_forecasting_fallback(forecast_df):
    result = run_xai_explanation(forecast_df, target_column="revenue", date_column="date")
    assert result["available"] is False
    assert result["global_explanation"] == FALLBACK_MESSAGE


def test_xai_uses_automl_best_model(regression_df):
    automl = run_automl(regression_df, target_column="revenue")
    result = run_xai_explanation(regression_df, automl_result=automl, target_column="revenue")
    assert result["model_name"] == automl["best_model"]["model_name"]
