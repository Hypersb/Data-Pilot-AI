from typing import Any

from fastapi import APIRouter

from app.routers.profile import _get_df
from app.services.analysis_service import build_analysis_bundle
from app.services.session_store import session_store

router = APIRouter(prefix="/api/sessions", tags=["analysis"])


@router.get("/{session_id}/analysis")
async def get_analysis(session_id: str) -> dict[str, Any]:
    cached = session_store.get_analysis_cache(session_id)
    if cached is not None:
        return cached

    df = _get_df(session_id)
    bundle = build_analysis_bundle(df)
    session_store.set_analysis_cache(session_id, bundle)
    return bundle
