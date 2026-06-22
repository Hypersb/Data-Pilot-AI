from fastapi import APIRouter

from app.routers.profile import _get_df
from app.schemas.v2_responses import SqlRequest, SqlResponse
from app.services.session_store import session_store
from app.services.sql_generation_service import generate_sql

router = APIRouter(prefix="/api/sessions", tags=["sql"])


@router.post("/{session_id}/sql", response_model=SqlResponse)
async def generate_sql_query(session_id: str, body: SqlRequest) -> SqlResponse:
    df = _get_df(session_id)
    meta = session_store.get_meta(session_id)
    table_name = meta["filename"].rsplit(".", 1)[0] if meta else "dataset"
    result = generate_sql(df, body.question, table_name=table_name)
    return SqlResponse(**result)
