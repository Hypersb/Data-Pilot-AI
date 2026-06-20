from fastapi import APIRouter, HTTPException

from app.routers.profile import _get_df
from app.schemas.responses import AnomalyResponse
from app.services.anomaly_engine import detect_anomalies

router = APIRouter(prefix="/api/sessions", tags=["anomalies"])


@router.get("/{session_id}/anomalies", response_model=AnomalyResponse)
async def get_anomalies(session_id: str) -> AnomalyResponse:
    df = _get_df(session_id)
    result = detect_anomalies(df)
    if not result.get("available"):
        raise HTTPException(status_code=400, detail=result["plain_english_explanation"])
    return AnomalyResponse(**result)
