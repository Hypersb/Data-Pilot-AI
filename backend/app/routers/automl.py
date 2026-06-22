from fastapi import APIRouter, HTTPException

from app.routers.profile import _get_df
from app.schemas.responses import AutoMLRequest, AutoMLResponse
from app.services.automl_engine import run_automl
from app.services.experiment_tracker_service import experiment_tracker

router = APIRouter(prefix="/api/sessions", tags=["automl"])


@router.post("/{session_id}/automl", response_model=AutoMLResponse)
async def run_session_automl(session_id: str, body: AutoMLRequest) -> AutoMLResponse:
    df = _get_df(session_id)
    try:
        result = run_automl(
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
        notes="AutoML run",
    )
    return AutoMLResponse(**result)
