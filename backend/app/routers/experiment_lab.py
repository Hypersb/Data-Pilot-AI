from fastapi import APIRouter, HTTPException

from app.routers.profile import _get_df
from app.schemas.v2_responses import ExperimentLabResponse
from app.services.experiment_lab_service import run_experiment_lab
from app.services.experiment_tracker_service import experiment_tracker

router = APIRouter(prefix="/api/sessions", tags=["experiment-lab"])


@router.get("/{session_id}/experiments/lab", response_model=ExperimentLabResponse)
async def get_experiment_lab(session_id: str) -> ExperimentLabResponse:
    df = _get_df(session_id)
    try:
        result = run_experiment_lab(df)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    best = next(fs for fs in result["feature_sets"] if fs.get("is_best"))
    experiment_tracker.log_run(
        session_id=session_id,
        model_name=best["model_name"],
        task_type=result["task_type"],
        metrics=best["metrics"],
        notes=f"Experiment Lab — Feature Set {best['label']}",
    )
    return ExperimentLabResponse(**result)
