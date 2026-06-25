from __future__ import annotations

import time
from typing import Any

import numpy as np
import pandas as pd

from app.services.automl_engine import (
    _detect_feature_columns,
    _evaluate_classification_model,
    _evaluate_regression_model,
    _prepare_tabular_matrix,
    _rank_classification,
    _rank_regression,
    _select_best_model,
    detect_task,
)
from app.services.ingest import infer_column_types

MODEL_DESCRIPTIONS: dict[str, str] = {
    "Linear Regression": "Fits a linear relationship between features and target. Fast, interpretable baseline for continuous outcomes.",
    "Random Forest Regressor": "Ensemble of decision trees that captures non-linear patterns and feature interactions with robust generalization.",
    "XGBoost Regressor": "Gradient-boosted trees optimized for predictive accuracy on structured tabular data.",
    "LightGBM": "High-performance gradient boosting with leaf-wise growth — efficient on larger datasets with many features.",
    "Logistic Regression": "Linear classifier estimating class probabilities. Strong baseline for binary and multiclass problems.",
    "Random Forest Classifier": "Tree ensemble that handles non-linear decision boundaries and mixed feature types.",
    "XGBoost Classifier": "Boosted trees for classification with strong performance on imbalanced and complex datasets.",
}


def run_model_arena(
    df: pd.DataFrame,
    target_column: str | None = None,
    date_column: str | None = None,
) -> dict[str, Any]:
    detection = _detect_arena_task(df, target_column=target_column)

    if detection["task_type"] == "regression":
        leaderboard = _arena_regression(df, detection["target_column"], detection["feature_columns"])
        primary_metric = "r2"
    else:
        leaderboard = _arena_classification(df, detection["target_column"], detection["feature_columns"])
        primary_metric = "f1"

    if not leaderboard:
        raise ValueError("No models could be trained on this dataset.")

    best = _select_best_model(detection["task_type"], leaderboard)
    for entry in leaderboard:
        entry["is_best"] = entry["model_name"] == best["model_name"]
        entry["score"] = _primary_score(detection["task_type"], entry["metrics"])
        entry["description"] = MODEL_DESCRIPTIONS.get(entry["model_name"], "")

    why_won = _build_why_won(detection["task_type"], best, leaderboard, primary_metric)
    summary = _build_performance_summary(detection["task_type"], best, leaderboard)
    explanation = _build_model_explanation(detection["task_type"], best, detection)

    return {
        "task_type": detection["task_type"],
        "target_column": detection["target_column"],
        "feature_columns": detection["feature_columns"],
        "detection_reason": detection["detection_reason"],
        "primary_metric": primary_metric,
        "leaderboard": leaderboard,
        "best_model": {
            "model_name": best["model_name"],
            "metrics": best["metrics"],
            "rank": best.get("rank", 1),
            "description": MODEL_DESCRIPTIONS.get(best["model_name"], ""),
            "why_it_won": why_won,
        },
        "model_explanation": explanation,
        "performance_summary": summary,
        "models_trained": len(leaderboard),
    }


def _detect_arena_task(
    df: pd.DataFrame, target_column: str | None = None
) -> dict[str, Any]:
    column_types = infer_column_types(df)
    detection = detect_task(df, target_column=target_column, date_column=None)

    if detection.task_type == "forecasting":
        from app.services.automl_engine import _detect_target_column, _is_classification_target

        target = target_column or detection.target_column
        col_type = column_types.get(target, "numeric")
        target_series = df[target]
        if _is_classification_target(target_series, col_type, len(df)):
            features = _detect_feature_columns(df, target, column_types, classification=True)
            return {
                "task_type": "classification",
                "target_column": target,
                "feature_columns": features,
                "detection_reason": f"Classifying '{target}' ({target_series.nunique()} classes) using tabular features.",
            }
        features = _detect_feature_columns(df, target, column_types, classification=False)
        return {
            "task_type": "regression",
            "target_column": target,
            "feature_columns": features,
            "detection_reason": f"Predicting continuous '{target}' from {len(features)} feature columns.",
        }

    return {
        "task_type": detection.task_type,
        "target_column": detection.target_column,
        "feature_columns": detection.feature_columns,
        "detection_reason": detection.detection_reason,
    }


def _arena_regression(
    df: pd.DataFrame, target_column: str, feature_columns: list[str]
) -> list[dict[str, Any]]:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split

    X, y_raw, _ = _prepare_tabular_matrix(df, target_column, feature_columns)
    y = pd.to_numeric(pd.Series(y_raw), errors="coerce").to_numpy()
    mask = ~np.isnan(y)
    X, y = X[mask], y[mask]

    if len(y) < 10:
        raise ValueError("Need at least 10 rows for model comparison.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models: list[tuple[str, Any]] = [
        ("Linear Regression", LinearRegression()),
        ("Random Forest Regressor", RandomForestRegressor(n_estimators=100, random_state=42)),
    ]
    try:
        from xgboost import XGBRegressor

        models.append(
            (
                "XGBoost Regressor",
                XGBRegressor(n_estimators=100, random_state=42, verbosity=0, objective="reg:squarederror"),
            )
        )
    except ImportError:
        pass
    try:
        from lightgbm import LGBMRegressor

        models.append(
            (
                "LightGBM",
                LGBMRegressor(n_estimators=100, random_state=42, verbosity=-1),
            )
        )
    except ImportError:
        pass

    leaderboard: list[dict[str, Any]] = []
    for name, model in models:
        entry = _timed_regression(name, model, X_train, X_test, y_train, y_test)
        if entry and entry["status"] == "success":
            leaderboard.append(entry)
    return _rank_regression(leaderboard)


def _arena_classification(
    df: pd.DataFrame, target_column: str, feature_columns: list[str]
) -> list[dict[str, Any]]:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder

    X, y_raw, _ = _prepare_tabular_matrix(df, target_column, feature_columns)
    encoder = LabelEncoder()
    y = encoder.fit_transform(pd.Series(y_raw).astype(str))

    if len(y) < 10:
        raise ValueError("Need at least 10 rows for model comparison.")

    stratify = y if len(np.unique(y)) > 1 and min(np.bincount(y)) >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=stratify
    )

    models: list[tuple[str, Any]] = [
        ("Logistic Regression", LogisticRegression(max_iter=1000, random_state=42)),
        ("Random Forest Classifier", RandomForestClassifier(n_estimators=100, random_state=42)),
    ]
    try:
        from xgboost import XGBClassifier

        models.append(
            (
                "XGBoost Classifier",
                XGBClassifier(n_estimators=100, random_state=42, verbosity=0, eval_metric="logloss"),
            )
        )
    except ImportError:
        pass

    leaderboard: list[dict[str, Any]] = []
    for name, model in models:
        entry = _timed_classification(name, model, X_train, X_test, y_train, y_test)
        if entry and entry["status"] == "success":
            leaderboard.append(entry)
    return _rank_classification(leaderboard)


def _timed_regression(name, model, X_train, X_test, y_train, y_test) -> dict[str, Any] | None:
    try:
        t0 = time.perf_counter()
        model.fit(X_train, y_train)
        train_ms = round((time.perf_counter() - t0) * 1000, 2)
        t1 = time.perf_counter()
        preds = model.predict(X_test)
        pred_ms = round((time.perf_counter() - t1) * 1000, 2)
        entry = _evaluate_regression_model(name, model, X_train, X_test, y_train, y_test)
        if entry:
            entry["training_time_ms"] = train_ms
            entry["prediction_time_ms"] = pred_ms
        return entry
    except Exception as exc:
        return {"model_name": name, "metrics": {}, "status": "failed", "error": str(exc)}


def _timed_classification(name, model, X_train, X_test, y_train, y_test) -> dict[str, Any] | None:
    try:
        t0 = time.perf_counter()
        model.fit(X_train, y_train)
        train_ms = round((time.perf_counter() - t0) * 1000, 2)
        t1 = time.perf_counter()
        model.predict(X_test)
        pred_ms = round((time.perf_counter() - t1) * 1000, 2)
        entry = _evaluate_classification_model(name, model, X_train, X_test, y_train, y_test)
        if entry:
            entry["training_time_ms"] = train_ms
            entry["prediction_time_ms"] = pred_ms
        return entry
    except Exception as exc:
        return {"model_name": name, "metrics": {}, "status": "failed", "error": str(exc)}


def _primary_score(task_type: str, metrics: dict[str, float]) -> float:
    if task_type == "regression":
        return metrics.get("r2", 0.0)
    return metrics.get("f1", 0.0)


def _build_why_won(
    task_type: str, best: dict[str, Any], leaderboard: list[dict[str, Any]], metric: str
) -> str:
    best_val = best["metrics"].get(metric, 0)
    runners = [e for e in leaderboard if e["model_name"] != best["model_name"]]
    if not runners:
        return f"{best['model_name']} was the only successful model with {metric.upper()} of {best_val:.4f}."

    second = runners[0]
    second_val = second["metrics"].get(metric, 0)
    if task_type == "regression":
        delta = best_val - second_val
        return (
            f"{best['model_name']} achieved the highest R² ({best_val:.4f}), "
            f"outperforming {second['model_name']} by {delta:.4f}. "
            f"It best captures the variance in the target while maintaining reasonable error (RMSE {best['metrics'].get('rmse', 0):.2f})."
        )
    delta = best_val - second_val
    return (
        f"{best['model_name']} leads with F1 score {best_val:.4f} "
        f"({delta:.4f} above {second['model_name']}). "
        f"Balanced precision ({best['metrics'].get('precision', 0):.4f}) and recall ({best['metrics'].get('recall', 0):.4f}) make it the most reliable classifier."
    )


def _build_performance_summary(
    task_type: str, best: dict[str, Any], leaderboard: list[dict[str, Any]]
) -> str:
    n = len(leaderboard)
    if task_type == "regression":
        return (
            f"Compared {n} regression models on a held-out test set. "
            f"Best: {best['model_name']} — R² {best['metrics'].get('r2', 0):.4f}, "
            f"RMSE {best['metrics'].get('rmse', 0):.2f}, MAE {best['metrics'].get('mae', 0):.2f}."
        )
    return (
        f"Compared {n} classifiers on a held-out test set. "
        f"Best: {best['model_name']} — Accuracy {best['metrics'].get('accuracy', 0):.4f}, "
        f"F1 {best['metrics'].get('f1', 0):.4f}, Precision {best['metrics'].get('precision', 0):.4f}, "
        f"Recall {best['metrics'].get('recall', 0):.4f}."
    )


def _build_model_explanation(
    task_type: str, best: dict[str, Any], detection: dict[str, Any]
) -> str:
    desc = MODEL_DESCRIPTIONS.get(best["model_name"], "")
    task_label = "regression" if task_type == "regression" else "classification"
    return (
        f"Task: {task_label} on '{detection['target_column']}' using {len(detection['feature_columns'])} features. "
        f"{detection['detection_reason']} "
        f"Winner: {best['model_name']}. {desc}"
    )
