from fastapi import APIRouter, HTTPException

from app.routers.profile import _get_df
from app.schemas.v2_responses import (
    ExperimentItem,
    ExperimentLogRequest,
    ExperimentsListResponse,
)
from app.services.experiment_tracker_service import experiment_tracker

router = APIRouter(prefix="/api", tags=["experiments"])


@router.get("/sessions/{session_id}/experiments", response_model=ExperimentsListResponse)
async def list_experiments(session_id: str) -> ExperimentsListResponse:
    _get_df(session_id)
    runs = experiment_tracker.list_runs(session_id)
    items = [ExperimentItem(**r) for r in runs]
    return ExperimentsListResponse(experiments=items, count=len(items))


@router.post("/sessions/{session_id}/experiments", response_model=ExperimentItem)
async def log_experiment(session_id: str, body: ExperimentLogRequest) -> ExperimentItem:
    _get_df(session_id)
    run_id = experiment_tracker.log_run(
        session_id=session_id,
        model_name=body.model_name,
        task_type=body.task_type,
        hyperparameters=body.hyperparameters,
        metrics=body.metrics,
        notes=body.notes,
    )
    record = experiment_tracker.get_run(run_id)
    if not record:
        raise HTTPException(status_code=500, detail="Failed to log experiment.")
    return ExperimentItem(**record)


@router.get("/experiments/{run_id}", response_model=ExperimentItem)
async def get_experiment(run_id: str) -> ExperimentItem:
    record = experiment_tracker.get_run(run_id)
    if not record:
        raise HTTPException(status_code=404, detail="Experiment run not found.")
    return ExperimentItem(**record)
