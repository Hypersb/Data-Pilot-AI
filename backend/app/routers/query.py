from fastapi import APIRouter

from app.routers.profile import _get_df
from app.schemas.responses import QueryRequest, QueryResponse
from app.services.nlq_engine import answer_query

router = APIRouter(prefix="/api/sessions", tags=["query"])


@router.post("/{session_id}/query", response_model=QueryResponse)
async def query(session_id: str, body: QueryRequest) -> QueryResponse:
    df = _get_df(session_id)
    result = await answer_query(df, body.question)
    return QueryResponse(**result)
