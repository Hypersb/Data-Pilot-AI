from fastapi import APIRouter, HTTPException, Query

from app.routers.profile import _get_df
from app.schemas.responses import ForecastLeaderboardResponse, ForecastRequest, ForecastResponse
from app.services.forecast_engine import run_forecast, run_forecast_leaderboard

router = APIRouter(prefix="/api/sessions", tags=["forecast"])


@router.get("/{session_id}/forecast", response_model=ForecastLeaderboardResponse)
async def get_forecast_leaderboard(
    session_id: str,
    target_column: str | None = Query(default=None),
    date_column: str | None = Query(default=None),
    forecast_horizon: int = Query(default=6, ge=1, le=24),
) -> ForecastLeaderboardResponse:
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
