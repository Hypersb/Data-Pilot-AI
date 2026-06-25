from fastapi import APIRouter, HTTPException

from app.routers.profile import _get_df
from app.schemas.responses import AutoMLRequest, ModelArenaResponse
from app.services.experiment_tracker_service import experiment_tracker
from app.services.model_arena_service import run_model_arena

router = APIRouter(prefix="/api/sessions", tags=["model-arena"])


@router.get("/{session_id}/models", response_model=ModelArenaResponse)
async def get_model_arena(session_id: str) -> ModelArenaResponse:
    df = _get_df(session_id)
    try:
        result = run_model_arena(df)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    experiment_tracker.log_run(
        session_id=session_id,
        model_name=result["best_model"]["model_name"],
        task_type=result["task_type"],
        metrics=result["best_model"]["metrics"],
        notes="Model Arena run",
    )
    return ModelArenaResponse(**result)


@router.post("/{session_id}/models", response_model=ModelArenaResponse)
async def run_model_arena_endpoint(
    session_id: str, body: AutoMLRequest
) -> ModelArenaResponse:
    df = _get_df(session_id)
    try:
        result = run_model_arena(
            df,
            target_column=body.target_column,
            date_column=body.date_column,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    experiment_tracker.log_run(
        session_id=session_id,
        model_name=result["best_model"]["model_name"],
        task_type=result["task_type"],
        metrics=result["best_model"]["metrics"],
        notes="Model Arena run",
    )
    return ModelArenaResponse(**result)
