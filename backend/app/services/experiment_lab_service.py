from __future__ import annotations

from typing import Any

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

from app.services.automl_engine import _detect_feature_columns, _is_classification_target
from app.services.ingest import infer_column_types

FEATURE_SET_LABELS = {
    "A": "Full feature set",
    "B": "Top correlated features",
    "C": "Numeric features only",
}


def run_experiment_lab(df: pd.DataFrame, target_column: str | None = None) -> dict[str, Any]:
    column_types = infer_column_types(df)
    target = _resolve_target(df, target_column, column_types)
    if not target:
        raise ValueError("Could not detect a target column for experiments.")

    col_type = column_types.get(target, "numeric")
    target_series = df[target]
    is_classification = _is_classification_target(target_series, col_type, len(df))
    task_type = "classification" if is_classification else "regression"

    all_features = _detect_feature_columns(
        df, target, column_types, classification=is_classification
    )
    if len(all_features) < 1:
        raise ValueError("Not enough features for experiment comparison.")

    feature_sets = _build_feature_sets(df, target, all_features, column_types, is_classification)

    results: list[dict[str, Any]] = []
    for label, features in feature_sets.items():
        if not features:
            continue
        try:
            entry = _run_feature_set_experiment(
                df, target, features, task_type, label
            )
            results.append(entry)
        except ValueError:
            continue

    if not results:
        raise ValueError("No feature set experiments could be completed.")

    results.sort(key=lambda r: r["score"], reverse=True)
    for i, r in enumerate(results, start=1):
        r["rank"] = i
        r["is_best"] = i == 1

    best = results[0]
    return {
        "task_type": task_type,
        "target_column": target,
        "feature_sets": results,
        "best_feature_set": best["label"],
        "summary": (
            f"Compared {len(results)} feature configurations for {task_type} on '{target}'. "
            f"Best: Feature Set {best['label']} ({best['name']}) with "
            f"{'F1' if is_classification else 'R²'} {best['score']:.4f} using {best['model_name']}."
        ),
    }


def _resolve_target(
    df: pd.DataFrame, target_column: str | None, column_types: dict[str, str]
) -> str | None:
    if target_column and target_column in df.columns:
        return target_column
    from app.services.automl_engine import _detect_target_column

    return _detect_target_column(df, column_types)


def _build_feature_sets(
    df: pd.DataFrame,
    target: str,
    all_features: list[str],
    column_types: dict[str, str],
    is_classification: bool,
) -> dict[str, list[str]]:
    numeric_features = [f for f in all_features if column_types.get(f) == "numeric"]

    set_a = all_features[:]
    set_b = _top_correlated_features(df, target, all_features, max_features=max(3, len(all_features) // 2))
    set_c = numeric_features if numeric_features else all_features[: max(1, len(all_features) // 2)]

    return {"A": set_a, "B": set_b, "C": set_c}


def _top_correlated_features(
    df: pd.DataFrame, target: str, features: list[str], max_features: int
) -> list[str]:
    numeric_target = pd.to_numeric(df[target], errors="coerce")
    if numeric_target.notna().sum() < 5:
        return features[:max_features]

    scores: list[tuple[str, float]] = []
    for col in features:
        if col == target:
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        if series.notna().sum() < 5:
            continue
        corr = numeric_target.corr(series)
        if pd.notna(corr):
            scores.append((col, abs(corr)))

    if not scores:
        return features[:max_features]
    scores.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in scores[:max_features]]


def _prepare_matrix(
    df: pd.DataFrame, target: str, features: list[str]
) -> tuple[np.ndarray, np.ndarray]:
    work = df[features + [target]].copy().dropna(subset=[target])
    encoded: list[np.ndarray] = []
    for col in features:
        series = work[col]
        if pd.api.types.is_numeric_dtype(series):
            numeric = pd.to_numeric(series, errors="coerce")
            encoded.append(numeric.fillna(numeric.median()).to_numpy().reshape(-1, 1))
        else:
            encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
            values = series.astype(str).fillna("missing").to_numpy().reshape(-1, 1)
            encoded.append(encoder.fit_transform(values))
    X = np.hstack(encoded) if encoded else np.empty((len(work), 0))
    return X, work[target].to_numpy()


def _run_feature_set_experiment(
    df: pd.DataFrame,
    target: str,
    features: list[str],
    task_type: str,
    label: str,
) -> dict[str, Any]:
    X, y_raw = _prepare_matrix(df, target, features)
    if len(y_raw) < 10:
        raise ValueError("Insufficient rows.")

    if task_type == "classification":
        encoder = LabelEncoder()
        y = encoder.fit_transform(pd.Series(y_raw).astype(str))
        stratify = y if len(np.unique(y)) > 1 and min(np.bincount(y)) >= 2 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=stratify
        )
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model_name = "Random Forest Classifier"
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        avg = "binary" if len(np.unique(y)) == 2 else "weighted"
        metrics = {
            "accuracy": round(float(accuracy_score(y_test, preds)), 4),
            "precision": round(float(precision_score(y_test, preds, average=avg, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, preds, average=avg, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, preds, average=avg, zero_division=0)), 4),
        }
        score = metrics["f1"]
    else:
        y = pd.to_numeric(pd.Series(y_raw), errors="coerce").to_numpy()
        mask = ~np.isnan(y)
        X, y = X[mask], y[mask]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model_name = "Random Forest Regressor"
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        metrics = {
            "r2": round(float(r2_score(y_test, preds)), 4),
            "rmse": round(float(np.sqrt(mean_squared_error(y_test, preds))), 4),
            "mae": round(float(mean_absolute_error(y_test, preds)), 4),
        }
        score = metrics["r2"]

    return {
        "label": label,
        "name": FEATURE_SET_LABELS.get(label, f"Feature Set {label}"),
        "features": features,
        "feature_count": len(features),
        "model_name": model_name,
        "metrics": metrics,
        "score": score,
    }
