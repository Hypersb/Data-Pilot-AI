from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import shap
from sklearn.linear_model import LinearRegression, LogisticRegression

from app.services.automl_engine import TaskType, fit_best_tabular_model, run_automl

TOP_N = 10
MAX_SHAP_ROWS = 300
FALLBACK_MESSAGE = "Explainability is not available for this model or dataset."


def run_xai_explanation(
    df: pd.DataFrame,
    target_column: str | None = None,
    date_column: str | None = None,
    row_index: int | None = None,
    automl_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        return _run_xai_explanation(
            df,
            target_column=target_column,
            date_column=date_column,
            row_index=row_index,
            automl_result=automl_result,
        )
    except Exception:
        return _fallback_response(target_column)


def _run_xai_explanation(
    df: pd.DataFrame,
    target_column: str | None = None,
    date_column: str | None = None,
    row_index: int | None = None,
    automl_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if automl_result is None:
        automl_result = run_automl(df, target_column=target_column, date_column=date_column)

    task_type: TaskType = automl_result["task_type"]
    if task_type == "forecasting":
        raise ValueError(FALLBACK_MESSAGE)

    target = automl_result["target_column"]
    features = automl_result["feature_columns"]
    model_name = automl_result["best_model"]["model_name"]

    model, X, _y, feature_names, label_encoder = fit_best_tabular_model(
        df, task_type, target, features, model_name
    )

    if X.size == 0:
        raise ValueError(FALLBACK_MESSAGE)

    X_sample = _sample_matrix(X)
    shap_values = _compute_shap_values(model, X_sample, task_type)

    global_importance = _global_feature_importance(shap_values, feature_names)
    top_features = global_importance[:TOP_N]
    global_explanation = _build_global_explanation(target, top_features)

    local_row = 0 if row_index is None else max(0, min(row_index, len(X) - 1))
    local_explanations = [
        _local_explanation(
            model, X, feature_names, top_features, local_row, task_type, label_encoder
        )
    ]

    chart_data = {
        "importance_bar": _build_importance_chart(top_features, target),
        "summary_plot": _build_summary_plot(X_sample, shap_values, feature_names, top_features),
    }

    return {
        "available": True,
        "model_name": model_name,
        "task_type": task_type,
        "target_column": target,
        "top_features": top_features,
        "global_explanation": global_explanation,
        "local_explanations": local_explanations,
        "chart_data": chart_data,
    }


def _fallback_response(target_column: str | None) -> dict[str, Any]:
    return {
        "available": False,
        "model_name": "",
        "task_type": "",
        "target_column": target_column or "",
        "top_features": [],
        "global_explanation": FALLBACK_MESSAGE,
        "local_explanations": [],
        "chart_data": {},
    }


def _sample_matrix(X: np.ndarray) -> np.ndarray:
    if len(X) <= MAX_SHAP_ROWS:
        return X
    rng = np.random.default_rng(42)
    indices = rng.choice(len(X), MAX_SHAP_ROWS, replace=False)
    return X[indices]


def _compute_shap_values(model: Any, X: np.ndarray, task_type: TaskType) -> np.ndarray:
    if _is_tree_model(model):
        values = shap.TreeExplainer(model).shap_values(X)
    elif _is_linear_model(model):
        values = shap.LinearExplainer(model, X).shap_values(X)
    else:
        values = shap.Explainer(model, X)(X).values

    if isinstance(values, list):
        values = values[1] if len(values) > 1 else values[0]
    if task_type == "classification" and getattr(values, "ndim", 0) == 3:
        values = np.abs(values).mean(axis=0)

    return np.asarray(values)


def _is_tree_model(model: Any) -> bool:
    name = type(model).__name__.lower()
    return any(k in name for k in ("forest", "xgb", "gradient", "extratrees", "decision"))


def _is_linear_model(model: Any) -> bool:
    return isinstance(model, (LinearRegression, LogisticRegression))


def _global_feature_importance(
    shap_values: np.ndarray, feature_names: list[str]
) -> list[dict[str, Any]]:
    mean_abs = np.abs(shap_values).mean(axis=0)
    mean_signed = shap_values.mean(axis=0)

    entries = []
    for name, importance, signed in zip(feature_names, mean_abs, mean_signed):
        entries.append(
            {
                "feature": name,
                "display_name": _prettify_feature_name(name),
                "importance": round(float(importance), 6),
                "direction": "positive" if signed >= 0 else "negative",
                "mean_shap_value": round(float(signed), 6),
            }
        )

    entries.sort(key=lambda item: item["importance"], reverse=True)
    for rank, entry in enumerate(entries, start=1):
        entry["rank"] = rank
    return entries


def _local_explanation(
    model: Any,
    X: np.ndarray,
    feature_names: list[str],
    top_features: list[dict[str, Any]],
    row_index: int,
    task_type: TaskType,
    label_encoder: Any,
) -> dict[str, Any]:
    row_shap = _compute_shap_values(model, X[row_index : row_index + 1], task_type)[0]
    prediction = model.predict(X[row_index : row_index + 1])[0]

    if label_encoder is not None:
        prediction_display = str(label_encoder.inverse_transform([int(prediction)])[0])
    else:
        prediction_display = round(float(prediction), 4)

    contributors = []
    for item in top_features[:TOP_N]:
        idx = feature_names.index(item["feature"])
        contributors.append(
            {
                "feature": item["feature"],
                "display_name": item["display_name"],
                "shap_value": round(float(row_shap[idx]), 6),
                "feature_value": _safe_feature_value(X[row_index, idx]),
            }
        )
    contributors.sort(key=lambda c: abs(c["shap_value"]), reverse=True)

    return {
        "row_index": row_index,
        "prediction": prediction_display,
        "top_contributors": contributors[:5],
        "narrative": _local_narrative(contributors[:3], prediction_display, task_type),
    }


def _safe_feature_value(value: float) -> float | str:
    if isinstance(value, (float, np.floating)) and np.isfinite(value):
        return round(float(value), 4)
    return str(value)


def _build_global_explanation(target_column: str, top_features: list[dict[str, Any]]) -> str:
    target = _prettify_feature_name(target_column)
    if not top_features:
        return f"No strong drivers were identified for {target}."

    names = [item["display_name"] for item in top_features[:3]]
    if len(names) == 1:
        return f"The model predicts {target} mainly using {names[0]}."
    if len(names) == 2:
        return f"The model predicts {target} mainly using {names[0]} and {names[1]}."
    return f"The model predicts {target} mainly using {names[0]}, {names[1]}, and {names[2]}."


def _local_narrative(
    contributors: list[dict[str, Any]],
    prediction: Any,
    task_type: TaskType,
) -> str:
    if not contributors:
        return "No dominant local drivers identified for this prediction."

    parts = []
    for item in contributors[:3]:
        direction = "increases" if item["shap_value"] >= 0 else "decreases"
        parts.append(f"{item['display_name']} ({direction} impact)")

    outcome = "predicted class" if task_type == "classification" else "prediction"
    joined = ", ".join(parts[:-1]) + f", and {parts[-1]}" if len(parts) > 1 else parts[0]
    return f"For this row, the {outcome} of {prediction} is most influenced by {joined}."


def _prettify_feature_name(name: str) -> str:
    cleaned = name.replace("_", " ").replace("-", " ")
    return " ".join(word.capitalize() for word in cleaned.split())


def _build_importance_chart(top_features: list[dict[str, Any]], target: str) -> dict[str, Any]:
    labels = [item["display_name"] for item in reversed(top_features)]
    values = [item["importance"] for item in reversed(top_features)]
    colors = [
        "#6366f1" if item["direction"] == "positive" else "#a855f7"
        for item in reversed(top_features)
    ]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=colors),
            text=[f"{v:.4f}" for v in values],
            textposition="auto",
        )
    )
    fig.update_layout(
        title=f"Top Feature Importance for {_prettify_feature_name(target)}",
        xaxis_title="Mean |SHAP value|",
        yaxis_title="Feature",
        margin=dict(l=40, r=20, t=40, b=40),
        height=max(360, len(labels) * 36),
    )
    return json.loads(pio.to_json(fig))


def _build_summary_plot(
    X: np.ndarray,
    shap_values: np.ndarray,
    feature_names: list[str],
    top_features: list[dict[str, Any]],
) -> dict[str, Any]:
    traces = []
    for item in top_features[: min(8, len(top_features))]:
        idx = feature_names.index(item["feature"])
        traces.append(
            go.Scatter(
                x=X[:, idx],
                y=shap_values[:, idx],
                mode="markers",
                name=item["display_name"],
                marker=dict(size=6, opacity=0.65),
            )
        )

    fig = go.Figure(data=traces)
    fig.update_layout(
        title="SHAP Summary Plot (feature value vs SHAP impact)",
        xaxis_title="Feature value",
        yaxis_title="SHAP value",
        margin=dict(l=40, r=20, t=40, b=40),
        height=420,
    )
    return json.loads(pio.to_json(fig))
