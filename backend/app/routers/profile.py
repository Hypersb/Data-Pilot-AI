from fastapi import APIRouter, HTTPException

from app.schemas.responses import ProfileResponse
from app.services.profiler import profile_dataframe
from app.services.session_store import session_store

router = APIRouter(prefix="/api/sessions", tags=["profile"])


def _get_df(session_id: str):
    df = session_store.get(session_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    return df


@router.get("/{session_id}/profile", response_model=ProfileResponse)
async def get_profile(session_id: str) -> ProfileResponse:
    df = _get_df(session_id)
    profile = profile_dataframe(df)
    return ProfileResponse(**profile)
