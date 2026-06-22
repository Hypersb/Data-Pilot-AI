from fastapi import APIRouter, HTTPException

from app.routers.profile import _get_df
from app.schemas.v2_responses import CleanRequest, CleanResponse, CleanAuditItem
from app.services.cleaning_agent_service import apply_cleaning
from app.services.health_score_service import compute_health_score
from app.services.session_store import session_store

router = APIRouter(prefix="/api/sessions", tags=["cleaning"])


@router.post("/{session_id}/clean", response_model=CleanResponse)
async def clean_dataset(session_id: str, body: CleanRequest) -> CleanResponse:
    df = _get_df(session_id)
    meta = session_store.get_meta(session_id)
    filename = meta["filename"] if meta else "cleaned.csv"

    health_before = compute_health_score(df)["overall_score"]
    cleaned, audit = apply_cleaning(df, body.instruction)
    health_after = compute_health_score(cleaned)["overall_score"]
    preview = cleaned.head(5).fillna("").astype(str).to_dict(orient="records")

    new_session_id: str | None = None
    if body.replace_in_place:
        session_store.replace_df(session_id, cleaned)
        session_store.append_cleaning_history(session_id, audit)
        target_id = session_id
    else:
        lineage = session_store.get_lineage(session_id) or {"cleaning_history": []}
        history = lineage.get("cleaning_history", []) + audit
        new_session_id = session_store.create_from_df(
            cleaned,
            f"cleaned_{filename}",
            parent_session_id=session_id,
            cleaning_history=history,
        )
        target_id = new_session_id

    return CleanResponse(
        success=True,
        audit_trail=[CleanAuditItem(**a) for a in audit],
        new_session_id=new_session_id,
        rows=len(cleaned),
        columns=len(cleaned.columns),
        preview=preview,
        health_score_before=health_before,
        health_score_after=health_after,
        message=f"Cleaning applied to session {target_id}.",
    )
