from __future__ import annotations

from typing import Any, Callable

import numpy as np
import pandas as pd

from app.services.anomaly_engine import detect_anomalies
from app.services.automl_engine import run_automl
from app.services.forecast_engine import run_forecast_leaderboard
from app.services.ingest import infer_column_types
from app.services.insight_engine import generate_insights
from app.services.profiler import profile_dataframe
from app.services.viz_engine import build_bar_chart_from_series
from app.services.xai_engine import run_xai_explanation

ToolExecutor = Callable[[pd.DataFrame, dict[str, Any]], dict[str, Any]]


def execute_tool(df: pd.DataFrame, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    executor = TOOL_REGISTRY.get(tool_name)
    if executor is None:
        return _error_result(tool_name, f"Unknown tool: {tool_name}")
    try:
        return executor(df, arguments)
    except ValueError as exc:
        return _error_result(tool_name, str(exc))
    except Exception as exc:
        return _error_result(tool_name, f"Tool execution failed: {exc}")


def _error_result(tool_name: str, message: str) -> dict[str, Any]:
    return {
        "tool_name": tool_name,
        "success": False,
        "facts": [message],
        "data": {},
        "chart_data": {},
        "confidence": 0.2,
        "answer_template": message,
        "error": message,
    }


def _success(
    tool_name: str,
    facts: list[str],
    data: dict[str, Any],
    chart_data: dict[str, Any] | None = None,
    confidence: float = 0.92,
    answer_template: str | None = None,
) -> dict[str, Any]:
    return {
        "tool_name": tool_name,
        "success": True,
        "facts": facts,
        "data": data,
        "chart_data": chart_data or {},
        "confidence": confidence,
        "answer_template": answer_template or " ".join(facts),
        "error": None,
    }


def _column_lists(df: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    types = infer_column_types(df)
    numeric = [c for c, t in types.items() if t == "numeric"]
    categorical = [c for c, t in types.items() if t == "categorical"]
    datetime_cols = [c for c, t in types.items() if t == "datetime"]
    return numeric, categorical, datetime_cols


def _pick_column(
    df: pd.DataFrame,
    requested: str | None,
    candidates: list[str],
    label: str,
) -> str:
    if requested:
        if requested not in df.columns:
            raise ValueError(f"Column '{requested}' not found in dataset.")
        return requested
    if not candidates:
        raise ValueError(f"No {label} column available in dataset.")
    return _prefer_business_column(candidates, label)


def _prefer_business_column(columns: list[str], kind: str) -> str:
    keywords = {
        "metric": ("revenue", "sales", "profit", "amount", "total", "value", "price"),
        "group": ("region", "state", "segment", "customer", "product", "category", "area"),
        "target": ("revenue", "sales", "profit", "amount", "total", "value"),
        "date": ("date", "time", "month", "period", "timestamp"),
    }
    for keyword in keywords.get(kind, ()):
        for col in columns:
            if keyword in col.lower():
                return col
    return columns[0]


def tool_summarize_dataset(df: pd.DataFrame, arguments: dict[str, Any]) -> dict[str, Any]:
    profile = profile_dataframe(df)
    types = infer_column_types(df)
    numeric, categorical, datetime_cols = _column_lists(df)
    facts = [
        f"Rows: {profile['rows']}",
        f"Columns: {profile['columns']}",
        f"Quality score: {profile['quality_score']}/100",
        f"Completeness: {profile['completeness_pct']}%",
        f"Numeric columns: {', '.join(numeric) if numeric else 'none'}",
        f"Categorical columns: {', '.join(categorical) if categorical else 'none'}",
        f"Datetime columns: {', '.join(datetime_cols) if datetime_cols else 'none'}",
    ]
    if profile["quality_flags"]:
        facts.append(f"Quality flags: {', '.join(profile['quality_flags'])}")
    answer = (
        f"This dataset has {profile['rows']} rows and {profile['columns']} columns. "
        f"Data quality score is {profile['quality_score']}/100 with "
        f"{profile['completeness_pct']}% completeness."
    )
    return _success(
        "summarize_dataset",
        facts,
        {"profile": profile, "column_types": types},
        confidence=0.98,
        answer_template=answer,
    )


def tool_top_n_by_metric(df: pd.DataFrame, arguments: dict[str, Any]) -> dict[str, Any]:
    numeric, categorical, _ = _column_lists(df)
    metric_col = _pick_column(df, arguments.get("metric_column"), numeric, "metric")
    group_col = _pick_column(df, arguments.get("group_column"), categorical, "group")
    n = int(arguments.get("n", 5))
    ascending = bool(arguments.get("ascending", False))

    grouped = (
        df.groupby(group_col, dropna=True)[metric_col]
        .apply(lambda s: pd.to_numeric(s, errors="coerce").sum())
        .sort_values(ascending=ascending)
    )
    top = grouped.head(n)
    if top.empty:
        raise ValueError(f"No aggregatable values for {group_col} and {metric_col}.")

    labels = [str(i) for i in top.index.tolist()]
    values = [round(float(v), 2) for v in top.values.tolist()]
    direction = "lowest" if ascending else "highest"
    leader = labels[0]
    leader_value = values[0]

    facts = [
        f"Grouped by '{group_col}' using total '{metric_col}'.",
        f"{direction.capitalize()} value: {leader} with {leader_value:,.2f}.",
    ]
    for idx, (label, value) in enumerate(zip(labels, values), start=1):
        facts.append(f"Rank {idx}: {label} = {value:,.2f}")

    chart = build_bar_chart_from_series(
        labels,
        values,
        f"{'Bottom' if ascending else 'Top'} {group_col} by {metric_col}",
    )
    answer = (
        f"{leader} has the {direction} {metric_col} at {leader_value:,.2f} "
        f"when grouped by {group_col}."
    )
    return _success(
        "top_n_by_metric",
        facts,
        {"group_column": group_col, "metric_column": metric_col, "rankings": list(top.items())},
        chart_data={"bar_chart": chart},
        answer_template=answer,
    )


def tool_compare_segments(df: pd.DataFrame, arguments: dict[str, Any]) -> dict[str, Any]:
    numeric, categorical, _ = _column_lists(df)
    segment_col = _pick_column(df, arguments.get("segment_column"), categorical, "group")
    metric_col = _pick_column(df, arguments.get("metric_column"), numeric, "metric")

    grouped = (
        df.groupby(segment_col, dropna=True)[metric_col]
        .apply(lambda s: pd.to_numeric(s, errors="coerce").mean())
        .sort_values(ascending=False)
    )
    if grouped.empty:
        raise ValueError(f"Unable to compare segments for {segment_col} and {metric_col}.")

    best = grouped.index[0]
    best_val = float(grouped.iloc[0])
    worst = grouped.index[-1]
    worst_val = float(grouped.iloc[-1])
    spread = best_val - worst_val

    facts = [
        f"Compared average {metric_col} across {segment_col}.",
        f"Best segment: {best} with average {metric_col} of {best_val:,.2f}.",
        f"Lowest segment: {worst} with average {metric_col} of {worst_val:,.2f}.",
        f"Spread between best and worst: {spread:,.2f}.",
    ]
    for segment, value in grouped.items():
        facts.append(f"{segment}: {float(value):,.2f}")

    labels = [str(i) for i in grouped.index.tolist()]
    values = [round(float(v), 2) for v in grouped.values.tolist()]
    chart = build_bar_chart_from_series(labels, values, f"Average {metric_col} by {segment_col}")
    answer = (
        f"The best-performing {segment_col} is {best} with an average {metric_col} of "
        f"{best_val:,.2f}, compared to {worst} at {worst_val:,.2f}."
    )
    return _success(
        "compare_segments",
        facts,
        {
            "segment_column": segment_col,
            "metric_column": metric_col,
            "segments": grouped.to_dict(),
            "best_segment": str(best),
        },
        chart_data={"bar_chart": chart},
        answer_template=answer,
    )


def tool_correlation_analysis(df: pd.DataFrame, arguments: dict[str, Any]) -> dict[str, Any]:
    numeric, _, _ = _column_lists(df)
    if len(numeric) < 2:
        raise ValueError("Need at least two numeric columns for correlation analysis.")

    target = arguments.get("target_column")
    target = _pick_column(df, target, numeric, "target") if target else numeric[0]
    numeric_df = df[numeric].apply(pd.to_numeric, errors="coerce")
    corr = numeric_df.corr()[target].drop(labels=[target], errors="ignore").dropna()
    if corr.empty:
        raise ValueError(f"No correlation values available for '{target}'.")

    corr = corr.reindex(corr.abs().sort_values(ascending=False).index)
    top_pairs = corr.head(5)
    facts = [f"Correlations with '{target}':"]
    for col, value in top_pairs.items():
        facts.append(f"{col}: r={float(value):.3f}")

    strongest_col = top_pairs.index[0]
    strongest_val = float(top_pairs.iloc[0])
    direction = "positively" if strongest_val > 0 else "negatively"
    answer = (
        f"'{strongest_col}' is most strongly {direction} correlated with '{target}' "
        f"(r={strongest_val:.3f})."
    )
    labels = [str(c) for c in top_pairs.index.tolist()]
    values = [round(float(v), 3) for v in top_pairs.values.tolist()]
    chart = build_bar_chart_from_series(labels, values, f"Correlation with {target}")
    return _success(
        "correlation_analysis",
        facts,
        {"target_column": target, "correlations": top_pairs.to_dict()},
        chart_data={"bar_chart": chart},
        answer_template=answer,
    )


def tool_anomaly_explanation(df: pd.DataFrame, arguments: dict[str, Any]) -> dict[str, Any]:
    result = detect_anomalies(df)
    if not result.get("available"):
        raise ValueError(result.get("plain_english_explanation", "Anomaly detection unavailable."))

    total = int(result.get("total_anomalies", 0))
    methods = result.get("anomaly_methods_used", [])
    explanation = result.get("plain_english_explanation", "")
    facts = [
        f"Anomaly methods used: {', '.join(methods) if methods else 'none'}.",
        f"Total anomalous rows detected: {total}.",
        explanation,
    ]
    rows = result.get("anomaly_rows", [])[:5]
    for row in rows:
        facts.append(
            f"Row {row['row_index']}: severity {row['severity']} via {', '.join(row['methods'])}."
        )

    answer = explanation
    if total == 0:
        answer = "No unusual records were detected in this dataset."
    return _success(
        "anomaly_explanation",
        facts,
        {"total_anomalies": total, "methods": methods, "sample_rows": rows},
        chart_data=result.get("chart_data", {}),
        confidence=0.9 if total else 0.85,
        answer_template=answer,
    )


def tool_forecast_metric(df: pd.DataFrame, arguments: dict[str, Any]) -> dict[str, Any]:
    numeric, _, datetime_cols = _column_lists(df)
    if not datetime_cols:
        raise ValueError("Forecasting requires a datetime column.")

    target = _pick_column(df, arguments.get("target_column"), numeric, "target")
    date_col = _pick_column(df, arguments.get("date_column"), datetime_cols, "date")
    horizon = int(arguments.get("horizon", 6))

    result = run_forecast_leaderboard(
        df,
        target_column=target,
        date_column=date_col,
        forecast_horizon=horizon,
    )
    best = result["best_model"]
    first_point = result["forecast"][0] if result["forecast"] else None
    facts = [
        result["explanation"],
        f"Best model: {best['model_name']} (MAPE {best['metrics']['mape']:.2f}%).",
        f"Forecast horizon: {horizon} periods.",
    ]
    if first_point:
        facts.append(
            f"Next forecast point ({first_point['date']}): {first_point['value']:,.2f} "
            f"(range {first_point['lower']:,.2f} – {first_point['upper']:,.2f})."
        )

    answer = result["explanation"]
    return _success(
        "forecast_metric",
        facts,
        {
            "target_column": target,
            "date_column": date_col,
            "best_model": best,
            "forecast": result["forecast"],
        },
        chart_data=result.get("chart_data", {}),
        confidence=0.93,
        answer_template=answer,
    )


def tool_model_explanation(df: pd.DataFrame, arguments: dict[str, Any]) -> dict[str, Any]:
    numeric, _, datetime_cols = _column_lists(df)
    target = _pick_column(df, arguments.get("target_column"), numeric, "target")
    date_col = arguments.get("date_column")
    if date_col and date_col not in df.columns:
        raise ValueError(f"Column '{date_col}' not found in dataset.")
    if not date_col and datetime_cols:
        date_col = datetime_cols[0]

    xai = run_xai_explanation(df, target_column=target, date_column=date_col)
    if not xai.get("available"):
        raise ValueError(xai.get("global_explanation", "Model explanation unavailable."))

    top = xai.get("top_features", [])[:5]
    facts = [xai["global_explanation"]]
    for item in top:
        facts.append(
            f"{item['display_name']}: importance {item['importance']:.4f} ({item['direction']})."
        )

    lead = top[0]["display_name"] if top else "features"
    answer = (
        f"The strongest driver of '{target}' is {lead}. "
        f"{xai['global_explanation']}"
    )
    return _success(
        "model_explanation",
        facts,
        {"target_column": target, "model_name": xai["model_name"], "top_features": top},
        chart_data=xai.get("chart_data", {}),
        confidence=0.91,
        answer_template=answer,
    )


def tool_generate_business_recommendation(
    df: pd.DataFrame, arguments: dict[str, Any]
) -> dict[str, Any]:
    focus = (arguments.get("focus_area") or "").strip()
    insights = generate_insights(df)
    if focus:
        focus_lower = focus.lower()
        insights = [
            i
            for i in insights
            if focus_lower in i["title"].lower()
            or focus_lower in i["description"].lower()
            or any(focus_lower in col.lower() for col in i.get("related_columns", []))
        ] or insights

    high = [i for i in insights if i["severity"] in ("high", "medium")][:5]
    if not high:
        high = insights[:3]

    facts = [f"Generated {len(high)} grounded recommendations from dataset insights."]
    recommendations: list[str] = []
    for item in high:
        line = f"{item['title']}: {item['description']}"
        facts.append(line)
        recommendations.append(item["description"])

    numeric, categorical, datetime_cols = _column_lists(df)
    if numeric and categorical:
        grouped = (
            df.groupby(categorical[0], dropna=True)[numeric[0]]
            .apply(lambda s: pd.to_numeric(s, errors="coerce").sum())
            .sort_values(ascending=False)
        )
        if not grouped.empty:
            facts.append(
                f"Prioritize {grouped.index[0]} — highest total {numeric[0]} "
                f"at {float(grouped.iloc[0]):,.2f}."
            )

    answer = " ".join(recommendations[:3]) if recommendations else "No actionable insights found."
    return _success(
        "generate_business_recommendation",
        facts,
        {"recommendations": recommendations, "insights_used": len(high)},
        confidence=0.88,
        answer_template=answer,
    )


TOOL_REGISTRY: dict[str, ToolExecutor] = {
    "summarize_dataset": tool_summarize_dataset,
    "top_n_by_metric": tool_top_n_by_metric,
    "compare_segments": tool_compare_segments,
    "correlation_analysis": tool_correlation_analysis,
    "anomaly_explanation": tool_anomaly_explanation,
    "forecast_metric": tool_forecast_metric,
    "model_explanation": tool_model_explanation,
    "generate_business_recommendation": tool_generate_business_recommendation,
}
