from fastapi import APIRouter, Query
from fastapi.responses import Response

from app.routers.profile import _get_df
from app.schemas.v2_responses import ReportV2Response
from app.services.report_service import generate_full_report
from app.services.session_store import session_store

router = APIRouter(prefix="/api/sessions", tags=["report-v2"])


@router.get("/{session_id}/report/v2", response_model=ReportV2Response)
async def get_report_v2(
    session_id: str,
    format: str = Query(default="markdown", pattern="^(markdown|pdf|pptx)$"),
) -> ReportV2Response | Response:
    df = _get_df(session_id)
    meta = session_store.get_meta(session_id)
    filename = meta["filename"] if meta else "dataset.csv"
    result = await generate_full_report(df, filename, fmt=format)  # type: ignore[arg-type]

    if format in ("pdf", "pptx"):
        media = "application/pdf" if format == "pdf" else (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        ext = format
        return Response(
            content=result["file_bytes"],
            media_type=media,
            headers={"Content-Disposition": f'attachment; filename="report.{ext}"'},
        )

    return ReportV2Response(
        markdown=result["markdown"],
        executive_summary=result["executive_summary"],
        scqa=result.get("scqa"),
        key_findings=result["key_findings"],
        risks=result["risks"],
        opportunities=result["opportunities"],
        recommendations=result["recommendations"],
        prioritized_recommendations=result.get("prioritized_recommendations", []),
        forecast_outlook=result.get("forecast_outlook", ""),
        llm_enhanced=result["llm_enhanced"],
        format=format,
    )
