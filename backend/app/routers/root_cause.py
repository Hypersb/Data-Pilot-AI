from fastapi import APIRouter

from app.routers.profile import _get_df
from app.schemas.v2_responses import RootCauseRequest, RootCauseResponse, ContributorItem
from app.services.root_cause_service import analyze_root_cause

router = APIRouter(prefix="/api/sessions", tags=["root-cause"])


@router.post("/{session_id}/root-cause", response_model=RootCauseResponse)
async def post_root_cause(session_id: str, body: RootCauseRequest) -> RootCauseResponse:
    df = _get_df(session_id)
    result = analyze_root_cause(
        df,
        metric_column=body.metric_column,
        dimension_columns=body.dimension_columns,
        period_column=body.period_column,
    )
    return RootCauseResponse(
        **{k: v for k, v in result.items() if k != "contributors"},
        contributors=[ContributorItem(**c) for c in result["contributors"]],
    )
