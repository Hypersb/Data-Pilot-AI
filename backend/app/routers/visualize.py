from fastapi import APIRouter

from app.routers.profile import _get_df
from app.schemas.responses import ChartItem, ChartsResponse
from app.services.viz_engine import generate_charts

router = APIRouter(prefix="/api/sessions", tags=["visualize"])


@router.get("/{session_id}/charts", response_model=ChartsResponse)
async def get_charts(session_id: str) -> ChartsResponse:
    df = _get_df(session_id)
    charts = generate_charts(df)
    items = [ChartItem(**c) for c in charts]
    return ChartsResponse(charts=items, count=len(items))
