import io

import pandas as pd
import pytest

from app.agents.agent_orchestrator import run_team_analysis
from app.agents.data_analyst_agent import run_data_analyst
from app.agents.qa_auditor_agent import run_qa_auditor

SAMPLE_CSV = b"""date,region,revenue
2024-01-01,North,100
2024-02-01,North,110
2024-03-01,South,90
2024-04-01,South,95
"""


def test_data_analyst_agent():
    df = pd.read_csv(io.BytesIO(SAMPLE_CSV))
    result = run_data_analyst(df)
    assert result["role"] == "data_analyst"
    assert len(result["findings"]) >= 1


def test_qa_auditor_agent():
    df = pd.read_csv(io.BytesIO(SAMPLE_CSV))
    result = run_qa_auditor(df)
    assert result["role"] == "qa_auditor"
    assert "health score" in result["findings"][0].lower()


@pytest.mark.asyncio
async def test_team_orchestrator():
    df = pd.read_csv(io.BytesIO(SAMPLE_CSV))
    result = await run_team_analysis(df, session_id="test")
    assert result["executive_summary"]
    assert result["analyst_section"]["role"] == "data_analyst"
    assert result["ml_section"]["role"] == "ml_engineer"
    assert result["business_section"]["role"] == "business_consultant"
    assert result["qa_section"]["role"] == "qa_auditor"
