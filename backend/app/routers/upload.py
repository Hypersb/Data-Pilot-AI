from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.schemas.responses import MessageResponse, UploadResponse
from app.services.ingest import dataframe_preview, infer_column_types, parse_upload
from app.services.session_store import session_store

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.max_upload_mb} MB.",
        )
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        df = parse_upload(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    session_id = session_store.create(df, file.filename)
    column_types = infer_column_types(df)

    return UploadResponse(
        session_id=session_id,
        filename=file.filename,
        rows=len(df),
        columns=list(df.columns),
        preview=dataframe_preview(df),
        column_types=column_types,
    )


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def delete_session(session_id: str) -> MessageResponse:
    if session_store.delete(session_id):
        return MessageResponse(message="Session deleted.")
    raise HTTPException(status_code=404, detail="Session not found or expired.")
