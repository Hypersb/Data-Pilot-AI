from fastapi import APIRouter, HTTPException

from app.routers.profile import _get_df
from app.schemas.v2_responses import (
    DatasetCompareRequest,
    DatasetCompareResponse,
    PeriodCompareRequest,
    PeriodCompareResponse,
    PeriodChangeItem,
)
from app.services.comparison_service import compare_datasets, compare_periods
from app.services.session_store import session_store

router = APIRouter(prefix="/api/sessions", tags=["comparison"])


@router.post("/{session_id}/compare/period", response_model=PeriodCompareResponse)
async def compare_period(session_id: str, body: PeriodCompareRequest) -> PeriodCompareResponse:
    df = _get_df(session_id)
    result = compare_periods(
        df,
        metric_column=body.metric_column,
        date_column=body.date_column,
        period=body.period,
    )
    return PeriodCompareResponse(
        **{k: v for k, v in result.items() if k != "changes"},
        changes=[PeriodChangeItem(**c) for c in result["changes"]],
    )


@router.post("/compare", response_model=DatasetCompareResponse)
async def compare_two_datasets(body: DatasetCompareRequest) -> DatasetCompareResponse:
    pair = session_store.compare_sessions(body.session_id_a, body.session_id_b)
    if pair is None:
        raise HTTPException(status_code=404, detail="One or both sessions not found or expired.")
    df_a, df_b = pair
    result = compare_datasets(
        df_a, df_b,
        session_id_a=body.session_id_a,
        session_id_b=body.session_id_b,
        metric_columns=body.metric_columns,
    )
    return DatasetCompareResponse(**result)
