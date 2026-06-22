from fastapi import APIRouter

from app.routers.profile import _get_df
from app.schemas.v2_responses import HealthResponse, HealthSubScores, HealthIssue
from app.services.health_score_service import compute_health_score

router = APIRouter(prefix="/api/sessions", tags=["health"])


@router.get("/{session_id}/health", response_model=HealthResponse)
async def get_health(session_id: str) -> HealthResponse:
    df = _get_df(session_id)
    result = compute_health_score(df)
    return HealthResponse(
        overall_score=result["overall_score"],
        sub_scores=HealthSubScores(**result["sub_scores"]),
        issues=[HealthIssue(**i) for i in result["issues"]],
        recommended_fixes=result["recommended_fixes"],
        rows=result["rows"],
        columns=result["columns"],
    )
