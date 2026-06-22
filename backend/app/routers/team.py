from fastapi import APIRouter

from app.agents.agent_orchestrator import run_team_analysis
from app.routers.profile import _get_df
from app.schemas.v2_responses import AgentFinding, TeamAnalysisResponse

router = APIRouter(prefix="/api/sessions", tags=["team"])


@router.post("/{session_id}/team-analysis", response_model=TeamAnalysisResponse)
async def team_analysis(session_id: str) -> TeamAnalysisResponse:
    df = _get_df(session_id)
    result = await run_team_analysis(df, session_id=session_id)
    return TeamAnalysisResponse(
        executive_summary=result["executive_summary"],
        analyst_section=AgentFinding(**result["analyst_section"]),
        ml_section=AgentFinding(**result["ml_section"]),
        business_section=AgentFinding(**result["business_section"]),
        qa_section=AgentFinding(**result["qa_section"]),
        combined_recommendations=result["combined_recommendations"],
    )
