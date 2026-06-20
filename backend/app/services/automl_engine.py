from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

from app.services.ingest import infer_column_types

TaskType = Literal["regression", "classification", "forecasting"]

TARGET_NAME_HINTS = (
    "target",
    "label",
    "class",
    "outcome",
    "churn",
    "revenue",
    "sales",
    "price",
    "amount",
    "y",
)

MIN_ROWS = 10
TEST_SIZE = 0.2
RANDOM_STATE = 42


@dataclass
class TaskDetection:
    task_type: TaskType
    target_column: str
    date_column: str | None
    feature_columns: list[str]
    detection_reason: str


def run_automl(
    df: pd.DataFrame,
    target_column: str | None = None,
    date_column: str | None = None,
) -> dict[str, Any]:
    detection = detect_task(df, target_column=target_column, date_column=date_column)

    if detection.task_type == "forecasting":
        leaderboard = _run_forecasting_leaderboard(
            df, detection.target_column, detection.date_column
        )
    elif detection.task_type == "classification":
        leaderboard = _run_classification_leaderboard(
            df, detection.target_column, detection.feature_columns
        )
    else:
        leaderboard = _run_regression_leaderboard(
            df, detection.target_column, detection.feature_columns
        )

    if not leaderboard:
        raise ValueError("No models could be trained on this dataset.")

    best = _select_best_model(detection.task_type, leaderboard)
    for entry in leaderboard:
        entry["is_best"] = entry["model_name"] == best["model_name"]

    return {
        "task_type": detection.task_type,
        "target_column": detection.target_column,
        "date_column": detection.date_column,
        "feature_columns": detection.feature_columns,
        "detection_reason": detection.detection_reason,
        "leaderboard": leaderboard,
        "best_model": best,
        "models_trained": len(leaderboard),
    }


def detect_task(
    df: pd.DataFrame,
    target_column: str | None = None,
    date_column: str | None = None,
) -> TaskDetection:
    column_types = infer_column_types(df)

    if not target_column:
        target_column = _detect_target_column(df, column_types)
    if not target_column or target_column not in df.columns:
        raise ValueError("Could not detect a valid target column for AutoML.")

    if not date_column:
        datetime_cols = [c for c, t in column_types.items() if t == "datetime"]
        date_column = datetime_cols[0] if datetime_cols else None

    if date_column and date_column in df.columns:
        ts = _prepare_timeseries(df, date_column, target_column)
        if len(ts) >= MIN_ROWS:
            return TaskDetection(
                task_type="forecasting",
                target_column=target_column,
                date_column=date_column,
                feature_columns=[],
                detection_reason=(
                    f"Detected datetime column '{date_column}' and numeric target "
                    f"'{target_column}' with {len(ts)} time points."
                ),
            )

    target_series = df[target_column]
    n_unique = target_series.nunique(dropna=True)
    col_type = column_types.get(target_column, "numeric")

    if _is_classification_target(target_series, col_type, len(df)):
        features = _detect_feature_columns(df, target_column, column_types, classification=True)
        return TaskDetection(
            task_type="classification",
            target_column=target_column,
            date_column=None,
            feature_columns=features,
            detection_reason=(
                f"Target '{target_column}' has {n_unique} unique classes/labels."
            ),
        )

    features = _detect_feature_columns(df, target_column, column_types, classification=False)
    if not features:
        raise ValueError("Not enough feature columns for regression AutoML.")

    return TaskDetection(
        task_type="regression",
        target_column=target_column,
        date_column=None,
        feature_columns=features,
        detection_reason=(
            f"Target '{target_column}' is numeric/continuous with "
            f"{pd.to_numeric(target_series, errors='coerce').nunique(dropna=True)} unique values."
        ),
    )


def _is_classification_target(series: pd.Series, col_type: str, row_count: int) -> bool:
    n_unique = series.nunique(dropna=True)
    if n_unique < 2 or n_unique > 20:
        return False
    if col_type == "categorical":
        return True

    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return False

    is_integer_like = np.allclose(numeric, numeric.round())
    if not is_integer_like:
        return False

    return n_unique <= min(20, max(2, row_count // 2))


def _detect_target_column(df: pd.DataFrame, column_types: dict[str, str]) -> str | None:
    for hint in TARGET_NAME_HINTS:
        for col in df.columns:
            if hint in col.lower():
                return col

    numeric_cols = [c for c, t in column_types.items() if t == "numeric"]
    non_id = [c for c in numeric_cols if "id" not in c.lower()]
    if non_id:
        return non_id[-1]

    categorical = [c for c, t in column_types.items() if t == "categorical"]
    if categorical:
        return categorical[-1]

    return numeric_cols[-1] if numeric_cols else None


def _detect_feature_columns(
    df: pd.DataFrame,
    target_column: str,
    column_types: dict[str, str],
    classification: bool,
) -> list[str]:
    features: list[str] = []
    for col in df.columns:
        if col == target_column:
            continue
        col_type = column_types.get(col, "text")
        if col_type in ("numeric", "categorical"):
            features.append(col)
        elif col_type == "datetime" and not classification:
            features.append(col)
    return features


def _prepare_timeseries(
    df: pd.DataFrame, date_column: str, target_column: str
) -> pd.DataFrame:
    work = df[[date_column, target_column]].copy()
    work[date_column] = pd.to_datetime(work[date_column], errors="coerce")
    work[target_column] = pd.to_numeric(work[target_column], errors="coerce")
    work = work.dropna().sort_values(date_column)
    return work.groupby(date_column, as_index=False)[target_column].sum()


def _prepare_tabular_matrix(
    df: pd.DataFrame, target_column: str, feature_columns: list[str]
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    work = df[feature_columns + [target_column]].copy()
    work = work.dropna(subset=[target_column])

    encoded_parts: list[np.ndarray] = []
    names: list[str] = []

    for col in feature_columns:
        series = work[col]
        if pd.api.types.is_numeric_dtype(series):
            numeric = pd.to_numeric(series, errors="coerce")
            encoded_parts.append(numeric.fillna(numeric.median()).to_numpy().reshape(-1, 1))
            names.append(col)
        else:
            encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
            values = series.astype(str).fillna("missing").to_numpy().reshape(-1, 1)
            encoded = encoder.fit_transform(values)
            encoded_parts.append(encoded)
            names.extend([f"{col}_{cat}" for cat in encoder.categories_[0]])

    X = np.hstack(encoded_parts) if encoded_parts else np.empty((len(work), 0))
    y = work[target_column]
    return X, y.to_numpy(), names


def _run_regression_leaderboard(
    df: pd.DataFrame, target_column: str, feature_columns: list[str]
) -> list[dict[str, Any]]:
    X, y_raw, _ = _prepare_tabular_matrix(df, target_column, feature_columns)
    y = pd.to_numeric(pd.Series(y_raw), errors="coerce").to_numpy()
    mask = ~np.isnan(y)
    X, y = X[mask], y[mask]

    if len(y) < MIN_ROWS:
        raise ValueError(f"Need at least {MIN_ROWS} rows for regression AutoML.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    models: list[tuple[str, Any]] = [
        ("Linear Regression", LinearRegression()),
        ("Random Forest Regressor", RandomForestRegressor(n_estimators=100, random_state=RANDOM_STATE)),
    ]

    try:
        from xgboost import XGBRegressor

        models.append(
            (
                "XGBoost Regressor",
                XGBRegressor(
                    n_estimators=100,
                    random_state=RANDOM_STATE,
                    verbosity=0,
                    objective="reg:squarederror",
                ),
            )
        )
    except ImportError:
        pass

    leaderboard: list[dict[str, Any]] = []
    for name, model in models:
        entry = _evaluate_regression_model(name, model, X_train, X_test, y_train, y_test)
        if entry and entry["status"] == "success":
            leaderboard.append(entry)

    return _rank_regression(leaderboard)


def _evaluate_regression_model(
    name: str,
    model: Any,
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> dict[str, Any] | None:
    try:
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        metrics = {
            "r2": round(float(r2_score(y_test, preds)), 4),
            "rmse": round(float(np.sqrt(mean_squared_error(y_test, preds))), 4),
            "mae": round(float(mean_absolute_error(y_test, preds)), 4),
        }
        return {"model_name": name, "metrics": metrics, "status": "success"}
    except Exception as exc:
        return {"model_name": name, "metrics": {}, "status": "failed", "error": str(exc)}


def _run_classification_leaderboard(
    df: pd.DataFrame, target_column: str, feature_columns: list[str]
) -> list[dict[str, Any]]:
    X, y_raw, _ = _prepare_tabular_matrix(df, target_column, feature_columns)
    y_series = pd.Series(y_raw).astype(str)
    encoder = LabelEncoder()
    y = encoder.fit_transform(y_series)

    if len(y) < MIN_ROWS:
        raise ValueError(f"Need at least {MIN_ROWS} rows for classification AutoML.")
    if len(encoder.classes_) < 2:
        raise ValueError("Classification requires at least 2 classes.")

    stratify = y if len(np.unique(y)) > 1 and min(np.bincount(y)) >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=stratify
    )

    models: list[tuple[str, Any]] = [
        ("Logistic Regression", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)),
        ("Random Forest Classifier", RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)),
    ]

    try:
        from xgboost import XGBClassifier

        models.append(
            (
                "XGBoost Classifier",
                XGBClassifier(
                    n_estimators=100,
                    random_state=RANDOM_STATE,
                    verbosity=0,
                    eval_metric="logloss",
                ),
            )
        )
    except ImportError:
        pass

    leaderboard: list[dict[str, Any]] = []
    for name, model in models:
        entry = _evaluate_classification_model(name, model, X_train, X_test, y_train, y_test)
        if entry and entry["status"] == "success":
            leaderboard.append(entry)

    return _rank_classification(leaderboard)


def _evaluate_classification_model(
    name: str,
    model: Any,
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> dict[str, Any] | None:
    try:
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        average = "binary" if len(np.unique(y_train)) == 2 else "weighted"
        metrics = {
            "accuracy": round(float(accuracy_score(y_test, preds)), 4),
            "precision": round(float(precision_score(y_test, preds, average=average, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, preds, average=average, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, preds, average=average, zero_division=0)), 4),
        }
        return {"model_name": name, "metrics": metrics, "status": "success"}
    except Exception as exc:
        return {"model_name": name, "metrics": {}, "status": "failed", "error": str(exc)}


def _run_forecasting_leaderboard(
    df: pd.DataFrame, target_column: str, date_column: str | None
) -> list[dict[str, Any]]:
    if not date_column:
        raise ValueError("Date column required for forecasting AutoML.")

    series_df = _prepare_timeseries(df, date_column, target_column)
    if len(series_df) < MIN_ROWS:
        raise ValueError(f"Need at least {MIN_ROWS} time points for forecasting AutoML.")

    split_idx = max(int(len(series_df) * (1 - TEST_SIZE)), MIN_ROWS // 2)
    train = series_df.iloc[:split_idx]
    test = series_df.iloc[split_idx:]
    if len(test) < 2:
        raise ValueError("Not enough holdout points for forecasting evaluation.")

    y_train = train[target_column].to_numpy()
    y_test = test[target_column].to_numpy()

    leaderboard: list[dict[str, Any]] = []

    arima_entry = _evaluate_arima_forecast(y_train, y_test)
    if arima_entry:
        leaderboard.append(arima_entry)

    prophet_entry = _evaluate_prophet_forecast(train, test, date_column, target_column)
    if prophet_entry:
        leaderboard.append(prophet_entry)

    return _rank_forecasting(leaderboard)


def _evaluate_arima_forecast(y_train: np.ndarray, y_test: np.ndarray) -> dict[str, Any] | None:
    try:
        from statsmodels.tsa.arima.model import ARIMA

        model = ARIMA(y_train, order=(1, 1, 1))
        fitted = model.fit()
        preds = fitted.forecast(steps=len(y_test))
        metrics = _forecast_metrics(y_test, preds)
        return {"model_name": "ARIMA", "metrics": metrics, "status": "success"}
    except Exception as exc:
        return {"model_name": "ARIMA", "metrics": {}, "status": "failed", "error": str(exc)}


def _evaluate_prophet_forecast(
    train: pd.DataFrame,
    test: pd.DataFrame,
    date_column: str,
    target_column: str,
) -> dict[str, Any] | None:
    try:
        from prophet import Prophet

        prophet_train = train.rename(columns={date_column: "ds", target_column: "y"})
        model = Prophet(daily_seasonality=False, weekly_seasonality=False, yearly_seasonality=False)
        model.fit(prophet_train[["ds", "y"]])

        future = test[[date_column]].rename(columns={date_column: "ds"})
        forecast = model.predict(future)
        preds = forecast["yhat"].to_numpy()
        metrics = _forecast_metrics(test[target_column].to_numpy(), preds)
        return {"model_name": "Prophet", "metrics": metrics, "status": "success"}
    except Exception as exc:
        return {"model_name": "Prophet", "metrics": {}, "status": "failed", "error": str(exc)}


def _forecast_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mask = y_true != 0
    if mask.any():
        mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)
    else:
        mape = float("inf")
    return {"mape": round(mape, 4), "rmse": round(rmse, 4)}


def _rank_regression(leaderboard: list[dict[str, Any]]) -> list[dict[str, Any]]:
    successful = [e for e in leaderboard if e.get("status") == "success"]
    successful.sort(key=lambda e: e["metrics"]["r2"], reverse=True)
    for i, entry in enumerate(successful, start=1):
        entry["rank"] = i
    return successful


def _rank_classification(leaderboard: list[dict[str, Any]]) -> list[dict[str, Any]]:
    successful = [e for e in leaderboard if e.get("status") == "success"]
    successful.sort(key=lambda e: e["metrics"]["f1"], reverse=True)
    for i, entry in enumerate(successful, start=1):
        entry["rank"] = i
    return successful


def _rank_forecasting(leaderboard: list[dict[str, Any]]) -> list[dict[str, Any]]:
    successful = [e for e in leaderboard if e.get("status") == "success"]
    successful.sort(key=lambda e: e["metrics"]["mape"])
    for i, entry in enumerate(successful, start=1):
        entry["rank"] = i
    return successful


def _select_best_model(task_type: TaskType, leaderboard: list[dict[str, Any]]) -> dict[str, Any]:
    successful = [e for e in leaderboard if e.get("status") == "success" and e.get("metrics")]
    if not successful:
        raise ValueError("All models failed to train.")

    if task_type == "regression":
        best = max(successful, key=lambda e: e["metrics"]["r2"])
    elif task_type == "classification":
        best = max(successful, key=lambda e: e["metrics"]["f1"])
    else:
        best = min(successful, key=lambda e: e["metrics"]["mape"])

    return {"model_name": best["model_name"], "metrics": best["metrics"], "rank": best.get("rank", 1)}


def create_model(task_type: TaskType, model_name: str) -> Any:
    if task_type == "regression":
        registry = {
            "Linear Regression": LinearRegression(),
            "Random Forest Regressor": RandomForestRegressor(
                n_estimators=100, random_state=RANDOM_STATE
            ),
        }
        if model_name == "XGBoost Regressor":
            from xgboost import XGBRegressor

            return XGBRegressor(
                n_estimators=100,
                random_state=RANDOM_STATE,
                verbosity=0,
                objective="reg:squarederror",
            )
    elif task_type == "classification":
        registry = {
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
            "Random Forest Classifier": RandomForestClassifier(
                n_estimators=100, random_state=RANDOM_STATE
            ),
        }
        if model_name == "XGBoost Classifier":
            from xgboost import XGBClassifier

            return XGBClassifier(
                n_estimators=100,
                random_state=RANDOM_STATE,
                verbosity=0,
                eval_metric="logloss",
            )
    else:
        raise ValueError(f"Unsupported task type for model creation: {task_type}")

    if model_name not in registry:
        raise ValueError(f"Unknown model name '{model_name}' for task '{task_type}'.")
    return registry[model_name]


def fit_best_tabular_model(
    df: pd.DataFrame,
    task_type: TaskType,
    target_column: str,
    feature_columns: list[str],
    model_name: str,
) -> tuple[Any, np.ndarray, np.ndarray, list[str], LabelEncoder | None]:
    if task_type not in ("regression", "classification"):
        raise ValueError("SHAP explanations require regression or classification AutoML tasks.")

    X, y_raw, feature_names = _prepare_tabular_matrix(df, target_column, feature_columns)
    label_encoder: LabelEncoder | None = None

    if task_type == "classification":
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(pd.Series(y_raw).astype(str))
    else:
        y = pd.to_numeric(pd.Series(y_raw), errors="coerce").to_numpy()
        mask = ~np.isnan(y)
        X, y = X[mask], y[mask]

    if len(y) < MIN_ROWS:
        raise ValueError(f"Need at least {MIN_ROWS} rows to train the best model.")

    model = create_model(task_type, model_name)
    model.fit(X, y)
    return model, X, y, feature_names, label_encoder
