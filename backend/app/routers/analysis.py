from typing import Any

from fastapi import APIRouter

from app.routers.profile import _get_df
from app.services.analysis_service import build_analysis_bundle

router = APIRouter(prefix="/api/sessions", tags=["analysis"])


@router.get("/{session_id}/analysis")
async def get_analysis(session_id: str) -> dict[str, Any]:
    df = _get_df(session_id)
    return build_analysis_bundle(df)
