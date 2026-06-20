from fastapi import APIRouter, HTTPException

from app.routers.profile import _get_df
from app.schemas.responses import ReportResponse
from app.services.report_engine import generate_report
from app.services.session_store import session_store

router = APIRouter(prefix="/api/sessions", tags=["report"])


@router.get("/{session_id}/report", response_model=ReportResponse)
async def get_report(session_id: str) -> ReportResponse:
    df = _get_df(session_id)
    meta = session_store.get_meta(session_id)
    filename = meta["filename"] if meta else "dataset"
    result = await generate_report(df, filename)
    return ReportResponse(markdown=result["markdown"], llm_enhanced=result["llm_enhanced"])
