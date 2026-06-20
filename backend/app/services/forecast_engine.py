from __future__ import annotations

import json
from typing import Any, Callable

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.services.ingest import infer_column_types

MIN_POINTS = 8
DEFAULT_HORIZON = 6
MAX_HORIZON = 24
LAG_FEATURES = 3


def run_forecast_leaderboard(
    df: pd.DataFrame,
    target_column: str | None = None,
    date_column: str | None = None,
    forecast_horizon: int = DEFAULT_HORIZON,
) -> dict[str, Any]:
    target_column, date_column = _resolve_columns(df, target_column, date_column)
    series_df = _prepare_series(df, date_column, target_column)
    forecast_horizon = max(1, min(forecast_horizon, MAX_HORIZON))

    if len(series_df) < MIN_POINTS:
        raise ValueError(
            f"Not enough data points for forecasting leaderboard (minimum {MIN_POINTS} required)."
        )

    y = series_df[target_column].to_numpy(dtype=float)
    dates = series_df[date_column]

    candidates = [
        ("ARIMA", _backtest_arima),
        ("Prophet", _backtest_prophet),
        ("Linear Regression", _backtest_linear_lags),
        ("XGBoost Regressor", _backtest_xgb_lags),
    ]

    leaderboard: list[dict[str, Any]] = []
    for model_name, backtest_fn in candidates:
        entry = _evaluate_model(model_name, backtest_fn, series_df, date_column, target_column, y)
        if entry and entry.get("status") == "success":
            leaderboard.append(entry)

    if not leaderboard:
        raise ValueError("All forecasting models failed. Unable to generate a leaderboard.")

    leaderboard = _rank_leaderboard(leaderboard)
    best = next(item for item in leaderboard if item.get("is_best"))
    forecast_block = _generate_best_forecast(
        best["model_name"],
        series_df,
        date_column,
        target_column,
        y,
        dates,
        forecast_horizon,
    )

    explanation = _build_explanation(best, leaderboard)
    chart_data = _build_chart(forecast_block["historical"], forecast_block["forecast"], target_column)

    return {
        "available": True,
        "target_column": target_column,
        "date_column": date_column,
        "forecast_horizon": forecast_horizon,
        "leaderboard": leaderboard,
        "best_model": best,
        "explanation": explanation,
        "historical": forecast_block["historical"],
        "forecast": forecast_block["forecast"],
        "chart_data": chart_data,
    }


def run_forecast(
    df: pd.DataFrame,
    target_column: str | None = None,
    date_column: str | None = None,
    periods: int = DEFAULT_HORIZON,
) -> dict[str, Any]:
    result = run_forecast_leaderboard(
        df,
        target_column=target_column,
        date_column=date_column,
        forecast_horizon=periods,
    )
    best = result["best_model"]
    return {
        "target_column": result["target_column"],
        "date_column": result["date_column"],
        "periods": result["forecast_horizon"],
        "model_used": best["model_name"],
        "metrics": best["metrics"],
        "historical": result["historical"],
        "forecast": result["forecast"],
    }


def _resolve_columns(
    df: pd.DataFrame, target_column: str | None, date_column: str | None
) -> tuple[str, str]:
    column_types = infer_column_types(df)
    datetime_cols = [c for c, t in column_types.items() if t == "datetime"]
    numeric_cols = [c for c, t in column_types.items() if t == "numeric"]

    if not target_column:
        target_column = numeric_cols[0] if numeric_cols else None
    if not date_column:
        date_column = datetime_cols[0] if datetime_cols else None

    if not target_column or target_column not in df.columns:
        raise ValueError("No valid target column found for forecasting.")
    if not date_column or date_column not in df.columns:
        raise ValueError("No valid date column found for forecasting.")
    return target_column, date_column


def _prepare_series(df: pd.DataFrame, date_column: str, target_column: str) -> pd.DataFrame:
    work = df[[date_column, target_column]].copy()
    work[date_column] = pd.to_datetime(work[date_column], errors="coerce")
    work[target_column] = pd.to_numeric(work[target_column], errors="coerce")
    work = work.dropna().sort_values(date_column)
    return work.groupby(date_column, as_index=False)[target_column].sum()


def _evaluate_model(
    model_name: str,
    backtest_fn: Callable[..., tuple[np.ndarray, np.ndarray] | None],
    series_df: pd.DataFrame,
    date_column: str,
    target_column: str,
    y: np.ndarray,
) -> dict[str, Any] | None:
    try:
        result = backtest_fn(series_df, date_column, target_column, y)
        if result is None:
            return {"model_name": model_name, "metrics": {}, "status": "failed"}
        actuals, preds = result
        metrics = _metrics(actuals, preds)
        return {"model_name": model_name, "metrics": metrics, "status": "success"}
    except Exception:
        return {"model_name": model_name, "metrics": {}, "status": "failed"}


def _rolling_windows(y: np.ndarray, horizon: int) -> list[tuple[np.ndarray, np.ndarray]]:
    horizon = max(1, min(horizon, 6))
    min_train = max(MIN_POINTS - 2, len(y) // 2)
    if len(y) < min_train + horizon:
        split = max(min_train, len(y) - horizon)
        return [(y[:split], y[split : split + horizon])]

    windows: list[tuple[np.ndarray, np.ndarray]] = []
    step = max(1, horizon)
    for end in range(min_train, len(y) - horizon + 1, step):
        windows.append((y[:end], y[end : end + horizon]))
    return windows[-3:] if len(windows) > 3 else windows


def _metrics(actuals: np.ndarray, preds: np.ndarray) -> dict[str, float]:
    actuals = np.asarray(actuals, dtype=float)
    preds = np.asarray(preds, dtype=float)
    rmse = float(np.sqrt(mean_squared_error(actuals, preds)))
    mae = float(mean_absolute_error(actuals, preds))
    mask = actuals != 0
    mape = float(np.mean(np.abs((actuals[mask] - preds[mask]) / actuals[mask])) * 100) if mask.any() else float("inf")
    return {"mape": round(mape, 4), "rmse": round(rmse, 4), "mae": round(mae, 4)}


def _backtest_arima(
    series_df: pd.DataFrame, date_column: str, target_column: str, y: np.ndarray
) -> tuple[np.ndarray, np.ndarray] | None:
    from statsmodels.tsa.arima.model import ARIMA

    horizon = max(1, min(3, len(y) // 4))
    actuals: list[float] = []
    preds: list[float] = []
    for train, test in _rolling_windows(y, horizon):
        if len(train) < 5:
            continue
        fitted = ARIMA(train, order=(1, 1, 1)).fit()
        forecast = fitted.forecast(steps=len(test))
        actuals.extend(test.tolist())
        preds.extend(np.asarray(forecast).tolist())
    if not actuals:
        return None
    return np.array(actuals), np.array(preds)


def _backtest_prophet(
    series_df: pd.DataFrame, date_column: str, target_column: str, y: np.ndarray
) -> tuple[np.ndarray, np.ndarray] | None:
    from prophet import Prophet

    horizon = max(1, min(3, len(y) // 4))
    actuals: list[float] = []
    preds: list[float] = []
    for train, test in _rolling_windows(y, horizon):
        train_df = series_df.iloc[: len(train)].rename(columns={date_column: "ds", target_column: "y"})
        model = Prophet(daily_seasonality=False, weekly_seasonality=False, yearly_seasonality=False)
        model.fit(train_df[["ds", "y"]])
        future = series_df.iloc[len(train) : len(train) + len(test)][[date_column]].rename(columns={date_column: "ds"})
        forecast = model.predict(future)
        actuals.extend(test.tolist())
        preds.extend(forecast["yhat"].to_numpy().tolist())
    if not actuals:
        return None
    return np.array(actuals), np.array(preds)


def _backtest_linear_lags(
    series_df: pd.DataFrame, date_column: str, target_column: str, y: np.ndarray
) -> tuple[np.ndarray, np.ndarray] | None:
    return _backtest_lag_model(y, LinearRegression())


def _backtest_xgb_lags(
    series_df: pd.DataFrame, date_column: str, target_column: str, y: np.ndarray
) -> tuple[np.ndarray, np.ndarray] | None:
    try:
        from xgboost import XGBRegressor
    except ImportError:
        return None
    model = XGBRegressor(n_estimators=50, random_state=42, verbosity=0, objective="reg:squarederror")
    return _backtest_lag_model(y, model)


def _backtest_lag_model(
    y: np.ndarray, model: Any
) -> tuple[np.ndarray, np.ndarray] | None:
    from sklearn.base import clone

    horizon = max(1, min(3, len(y) // 4))
    actuals: list[float] = []
    preds: list[float] = []
    for train, test in _rolling_windows(y, horizon):
        try:
            fitted = _fit_lag_model(train, clone(model))
        except ValueError:
            continue
        predicted = _recursive_lag_forecast(train, len(test), fitted)
        actuals.extend(test.tolist())
        preds.extend(predicted.tolist())
    if not actuals:
        return None
    return np.array(actuals), np.array(preds)


def _recursive_lag_forecast(train: np.ndarray, steps: int, model: Any) -> np.ndarray:
    history = train.tolist()
    predictions: list[float] = []
    for _ in range(steps):
        features = _lag_feature_row(history)
        if features is None:
            predictions.append(history[-1])
            history.append(history[-1])
            continue
        pred = float(model.predict(features.reshape(1, -1))[0])
        predictions.append(pred)
        history.append(pred)
    return np.array(predictions)


def _lag_feature_row(history: list[float]) -> np.ndarray | None:
    if len(history) < LAG_FEATURES + 1:
        return None
    lags = history[-LAG_FEATURES:][::-1]
    t = len(history)
    return np.array(lags + [t], dtype=float)


def _fit_lag_model(train: np.ndarray, model: Any) -> Any:
    rows: list[list[float]] = []
    targets: list[float] = []
    for idx in range(LAG_FEATURES, len(train)):
        row = _lag_feature_row(train[:idx].tolist())
        if row is not None:
            rows.append(row.tolist())
            targets.append(train[idx])
    if len(rows) < 2:
        raise ValueError("Insufficient history for lag model.")
    model.fit(np.array(rows), np.array(targets))
    return model


def _rank_leaderboard(leaderboard: list[dict[str, Any]]) -> list[dict[str, Any]]:
    successful = [entry for entry in leaderboard if entry.get("status") == "success"]
    successful.sort(key=lambda item: item["metrics"]["mape"])
    for rank, entry in enumerate(successful, start=1):
        entry["rank"] = rank
        entry["is_best"] = False
    if successful:
        successful[0]["is_best"] = True
    return successful


def _generate_best_forecast(
    model_name: str,
    series_df: pd.DataFrame,
    date_column: str,
    target_column: str,
    y: np.ndarray,
    dates: pd.Series,
    horizon: int,
) -> dict[str, Any]:
    if model_name == "ARIMA":
        return _forecast_arima_full(series_df, date_column, target_column, y, dates, horizon)
    if model_name == "Prophet":
        return _forecast_prophet_full(series_df, date_column, target_column, dates, horizon)
    if model_name == "Linear Regression":
        model = LinearRegression()
        return _forecast_lag_full(y, dates, horizon, model, model_name)
    if model_name == "XGBoost Regressor":
        from xgboost import XGBRegressor

        model = XGBRegressor(n_estimators=100, random_state=42, verbosity=0, objective="reg:squarederror")
        return _forecast_lag_full(y, dates, horizon, model, model_name)
    raise ValueError(f"Unsupported model: {model_name}")


def _future_dates(last_date: pd.Timestamp, periods: int, reference_dates: pd.Series) -> list[pd.Timestamp]:
    freq = pd.infer_freq(reference_dates)
    if freq:
        return list(pd.date_range(start=last_date, periods=periods + 1, freq=freq)[1:])
    delta = reference_dates.diff().median()
    if pd.isna(delta) or delta == pd.Timedelta(0):
        delta = pd.Timedelta(days=30)
    return [last_date + delta * (i + 1) for i in range(periods)]


def _forecast_arima_full(
    series_df: pd.DataFrame,
    date_column: str,
    target_column: str,
    y: np.ndarray,
    dates: pd.Series,
    horizon: int,
) -> dict[str, Any]:
    from statsmodels.tsa.arima.model import ARIMA

    fitted = ARIMA(y, order=(1, 1, 1)).fit()
    forecast_vals = fitted.forecast(steps=horizon)
    conf = fitted.get_forecast(steps=horizon).conf_int(alpha=0.2)
    if hasattr(conf, "iloc"):
        lower = conf.iloc[:, 0].to_numpy()
        upper = conf.iloc[:, 1].to_numpy()
    else:
        conf_arr = np.asarray(conf)
        lower = conf_arr[:, 0]
        upper = conf_arr[:, 1]
    future = _future_dates(pd.Timestamp(dates.iloc[-1]), horizon, dates)
    return _forecast_payload(series_df, date_column, target_column, future, forecast_vals, lower, upper)


def _forecast_prophet_full(
    series_df: pd.DataFrame,
    date_column: str,
    target_column: str,
    dates: pd.Series,
    horizon: int,
) -> dict[str, Any]:
    from prophet import Prophet

    train_df = series_df.rename(columns={date_column: "ds", target_column: "y"})
    model = Prophet(daily_seasonality=False, weekly_seasonality=False, yearly_seasonality=False)
    model.fit(train_df[["ds", "y"]])
    future = _future_dates(pd.Timestamp(dates.iloc[-1]), horizon, dates)
    future_df = pd.DataFrame({"ds": future})
    forecast = model.predict(future_df)
    lower = forecast["yhat_lower"].to_numpy()
    upper = forecast["yhat_upper"].to_numpy()
    return _forecast_payload(
        series_df,
        date_column,
        target_column,
        future,
        forecast["yhat"].to_numpy(),
        lower,
        upper,
    )


def _forecast_lag_full(
    y: np.ndarray, dates: pd.Series, horizon: int, model: Any, model_name: str
) -> dict[str, Any]:
    fitted = _fit_lag_model(y, model)
    rows: list[np.ndarray] = []
    targets: list[float] = []
    for idx in range(LAG_FEATURES, len(y)):
        row = _lag_feature_row(y[:idx].tolist())
        if row is not None:
            rows.append(row)
            targets.append(float(y[idx]))
    in_sample = fitted.predict(np.array(rows)) if rows else np.array([])
    std = float(np.std(np.array(targets) - in_sample)) if len(targets) > 1 else 0.0

    preds = _recursive_lag_forecast(y, horizon, fitted)
    lower = preds - 1.28 * std
    upper = preds + 1.28 * std
    future = _future_dates(pd.Timestamp(dates.iloc[-1]), horizon, dates)
    historical = [
        {"date": pd.Timestamp(d).strftime("%Y-%m-%d"), "value": round(float(v), 2)}
        for d, v in zip(dates, y)
    ]
    forecast = [
        {
            "date": pd.Timestamp(d).strftime("%Y-%m-%d"),
            "value": round(float(v), 2),
            "lower": round(float(lo), 2),
            "upper": round(float(hi), 2),
        }
        for d, v, lo, hi in zip(future, preds, lower, upper)
    ]
    return {"historical": historical, "forecast": forecast}


def _forecast_payload(
    series_df: pd.DataFrame,
    date_column: str,
    target_column: str,
    future_dates: list[pd.Timestamp],
    forecast_vals: Any,
    lower: Any,
    upper: Any,
) -> dict[str, Any]:
    historical = [
        {"date": row[date_column].strftime("%Y-%m-%d"), "value": round(float(row[target_column]), 2)}
        for _, row in series_df.iterrows()
    ]
    forecast = [
        {
            "date": pd.Timestamp(d).strftime("%Y-%m-%d"),
            "value": round(float(v), 2),
            "lower": round(float(lo), 2),
            "upper": round(float(hi), 2),
        }
        for d, v, lo, hi in zip(future_dates, forecast_vals, lower, upper)
    ]
    return {"historical": historical, "forecast": forecast}


def _build_explanation(best: dict[str, Any], leaderboard: list[dict[str, Any]]) -> str:
    mape = best["metrics"]["mape"]
    others = [entry["model_name"] for entry in leaderboard if entry["model_name"] != best["model_name"]]
    if not others:
        return f"{best['model_name']} achieved the best forecasting performance with a MAPE of {mape:.2f}%."
    if len(others) == 1:
        tail = others[0]
    elif len(others) == 2:
        tail = f"{others[0]} and {others[1]}"
    else:
        tail = ", ".join(others[:-1]) + f", and {others[-1]}"
    return (
        f"{best['model_name']} achieved the best forecasting performance with a MAPE of {mape:.2f}%, "
        f"outperforming {tail}."
    )


def _build_chart(historical: list[dict[str, Any]], forecast: list[dict[str, Any]], target: str) -> dict[str, Any]:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[point["date"] for point in historical],
            y=[point["value"] for point in historical],
            mode="lines+markers",
            name="Historical",
            line=dict(color="#6366f1"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[point["date"] for point in forecast],
            y=[point["value"] for point in forecast],
            mode="lines+markers",
            name="Forecast",
            line=dict(color="#a855f7", dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[point["date"] for point in forecast] + [point["date"] for point in forecast][::-1],
            y=[point["upper"] for point in forecast] + [point["lower"] for point in forecast][::-1],
            fill="toself",
            fillcolor="rgba(168, 85, 247, 0.15)",
            line=dict(color="rgba(168, 85, 247, 0)"),
            name="Confidence interval",
            showlegend=True,
        )
    )
    fig.update_layout(
        title=f"Forecast: {target}",
        xaxis_title="Date",
        yaxis_title=target,
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return {"forecast_chart": json.loads(pio.to_json(fig))}
