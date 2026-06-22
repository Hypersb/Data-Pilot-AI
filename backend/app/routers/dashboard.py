from fastapi import APIRouter

from app.routers.profile import _get_df
from app.schemas.v2_responses import DashboardResponse, KpiItem, DashboardPanel
from app.services.dashboard_service import generate_dashboard

router = APIRouter(prefix="/api/sessions", tags=["dashboard"])


@router.get("/{session_id}/dashboard", response_model=DashboardResponse)
async def get_dashboard(session_id: str) -> DashboardResponse:
    df = _get_df(session_id)
    result = generate_dashboard(df)
    return DashboardResponse(
        kpis=[KpiItem(**k) for k in result["kpis"]],
        panels=[DashboardPanel(**p) for p in result["panels"]],
        quality_alerts=result["quality_alerts"],
        chart_data=result["chart_data"],
    )
