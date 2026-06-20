from fastapi import APIRouter, HTTPException

from app.routers.profile import _get_df
from app.schemas.agent import ChatRequest, ChatResponse
from app.services.agent_engine import run_agent_chat

router = APIRouter(prefix="/api/sessions", tags=["chat"])


@router.post("/{session_id}/chat", response_model=ChatResponse)
async def chat(session_id: str, body: ChatRequest) -> ChatResponse:
    df = _get_df(session_id)
    try:
        result = await run_agent_chat(df, body.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ChatResponse(**result)
