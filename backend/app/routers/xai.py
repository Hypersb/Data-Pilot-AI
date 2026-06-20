from fastapi import APIRouter, HTTPException, Query

from app.routers.profile import _get_df
from app.schemas.responses import XAIResponse
from app.services.xai_engine import run_xai_explanation

router = APIRouter(prefix="/api/sessions", tags=["xai"])


@router.get("/{session_id}/xai", response_model=XAIResponse)
async def get_xai_explanation(
    session_id: str,
    target_column: str | None = Query(default=None),
    date_column: str | None = Query(default=None),
    row_index: int | None = Query(default=None, ge=0),
) -> XAIResponse:
    df = _get_df(session_id)
    result = run_xai_explanation(
        df,
        target_column=target_column,
        date_column=date_column,
        row_index=row_index,
    )
    if not result.get("available"):
        raise HTTPException(status_code=400, detail=result["global_explanation"])
    return XAIResponse(**result)
