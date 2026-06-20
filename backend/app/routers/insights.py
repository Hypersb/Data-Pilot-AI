from fastapi import APIRouter

from app.routers.profile import _get_df
from app.schemas.responses import InsightItem, InsightsResponse
from app.services.insight_engine import generate_insights

router = APIRouter(prefix="/api/sessions", tags=["insights"])


@router.get("/{session_id}/insights", response_model=InsightsResponse)
async def get_insights(session_id: str) -> InsightsResponse:
    df = _get_df(session_id)
    insights = generate_insights(df)
    items = [InsightItem(**i) for i in insights]
    return InsightsResponse(insights=items, count=len(items))
