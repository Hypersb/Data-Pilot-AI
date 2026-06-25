from fastapi import APIRouter, HTTPException, Query

from app.routers.profile import _get_df
from app.schemas.responses import ForecastLeaderboardResponse, ForecastRequest, ForecastResponse
from app.services.forecast_engine import run_forecast, run_forecast_leaderboard
from app.services.experiment_tracker_service import experiment_tracker
from app.services.session_store import session_store

router = APIRouter(prefix="/api/sessions", tags=["forecast"])


@router.get("/{session_id}/forecast", response_model=ForecastLeaderboardResponse)
async def get_forecast_leaderboard(
    session_id: str,
    target_column: str | None = Query(default=None),
    date_column: str | None = Query(default=None),
    forecast_horizon: int = Query(default=6, ge=1, le=24),
) -> ForecastLeaderboardResponse:
    cache_key = f"forecast:{target_column}:{date_column}:{forecast_horizon}"
    cached = session_store.get_ml_cache(session_id, cache_key)
    if cached is not None:
        return ForecastLeaderboardResponse(**cached)

    df = _get_df(session_id)
    try:
        result = run_forecast_leaderboard(
            df,
            target_column=target_column,
            date_column=date_column,
            forecast_horizon=forecast_horizon,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if result.get("available") and result.get("best_model"):
        experiment_tracker.log_run(
            session_id=session_id,
            model_name=result["best_model"]["model_name"],
            task_type="forecasting",
            metrics=result["best_model"].get("metrics", {}),
            notes="Forecast leaderboard run",
        )
    session_store.set_ml_cache(session_id, cache_key, result)
    return ForecastLeaderboardResponse(**result)


@router.post("/{session_id}/forecast", response_model=ForecastResponse)
async def forecast(session_id: str, body: ForecastRequest) -> ForecastResponse:
    df = _get_df(session_id)
    try:
        result = run_forecast(
            df,
            target_column=body.target_column,
            date_column=body.date_column,
            periods=body.periods,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ForecastResponse(**result)
