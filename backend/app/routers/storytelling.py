from fastapi import APIRouter, Query

from app.routers.profile import _get_df
from app.schemas.v2_responses import StoryResponse
from app.services.storytelling_service import generate_story

router = APIRouter(prefix="/api/sessions", tags=["storytelling"])


@router.get("/{session_id}/story", response_model=StoryResponse)
async def get_story(
    session_id: str,
    topic: str | None = Query(default=None),
) -> StoryResponse:
    df = _get_df(session_id)
    result = await generate_story(df, topic=topic)
    return StoryResponse(**result)
