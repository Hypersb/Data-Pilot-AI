import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.agent import AgentPlan
from app.services.agent_engine import heuristic_plan, run_agent_chat, validate_agent_plan
from app.services.agent_tools import execute_tool
from app.services.ingest import parse_upload

client = TestClient(app)

SALES_CSV = b"""date,region,product,revenue,profit
2024-01-01,North,A,100,20
2024-02-01,North,A,110,22
2024-03-01,North,A,120,24
2024-04-01,South,B,90,15
2024-05-01,South,B,95,16
2024-06-01,South,B,100,17
2024-07-01,East,A,130,26
2024-08-01,East,A,140,28
2024-09-01,West,B,150,30
2024-10-01,West,B,160,32
2024-11-01,North,C,170,34
2024-12-01,South,C,180,36
"""

REGRESSION_CSV = b"""feature_a,feature_b,profit
1.0,2.0,10.5
2.0,3.0,15.2
3.0,4.0,18.1
4.0,5.0,22.0
5.0,6.0,25.5
6.0,7.0,28.3
7.0,8.0,31.0
8.0,9.0,34.2
9.0,10.0,37.5
10.0,11.0,40.0
11.0,12.0,43.1
12.0,13.0,46.0
"""

ANOMALY_CSV = b"""date,value,score
2024-01-01,10,1
2024-02-01,11,1
2024-03-01,12,1
2024-04-01,13,1
2024-05-01,14,1
2024-06-01,15,1
2024-07-01,16,1
2024-08-01,17,1
2024-09-01,200,1
2024-10-01,18,1
2024-11-01,19,1
2024-12-01,20,1
"""


@pytest.fixture
def sales_df():
    return parse_upload(SALES_CSV, "sales.csv")


@pytest.fixture
def regression_df():
    return parse_upload(REGRESSION_CSV, "regression.csv")


@pytest.fixture
def anomaly_df():
    return parse_upload(ANOMALY_CSV, "anomaly.csv")


@pytest.mark.parametrize(
    ("question", "expected_tool"),
    [
        ("Which state generated the most revenue?", "top_n_by_metric"),
        ("Forecast next month's revenue.", "forecast_metric"),
        ("Show me unusual records.", "anomaly_explanation"),
        ("What variables influence profit most?", "model_explanation"),
        ("Which customer segment performs best?", "compare_segments"),
        ("Summarize this dataset.", "summarize_dataset"),
        ("What is the correlation with profit?", "correlation_analysis"),
        ("What caused sales to drop?", "generate_business_recommendation"),
    ],
)
def test_heuristic_tool_selection(sales_df, question, expected_tool):
    plan = heuristic_plan(question, sales_df)
    assert plan.tool_name == expected_tool


def test_agent_plan_validation():
    plan = validate_agent_plan(
        {"tool_name": "forecast_metric", "arguments": {"horizon": 3, "target_column": "revenue"}}
    )
    assert plan.tool_name == "forecast_metric"
    assert plan.arguments["horizon"] == 3


def test_agent_plan_rejects_unknown_tool():
    with pytest.raises(ValueError):
        validate_agent_plan({"tool_name": "run_python", "arguments": {}})


def test_agent_plan_rejects_invalid_horizon():
    with pytest.raises(ValueError):
        validate_agent_plan({"tool_name": "forecast_metric", "arguments": {"horizon": 100}})


def test_agent_plan_normalizes_aliases():
    plan = validate_agent_plan({"tool_name": "forecast", "arguments": {"horizon": 2}})
    assert plan.tool_name == "forecast_metric"


@pytest.mark.asyncio
async def test_summarize_tool(sales_df):
    result = execute_tool(sales_df, "summarize_dataset", {})
    assert result["success"] is True
    assert any("Rows:" in fact for fact in result["facts"])


@pytest.mark.asyncio
async def test_top_n_tool(sales_df):
    result = execute_tool(
        sales_df,
        "top_n_by_metric",
        {"metric_column": "revenue", "group_column": "region", "n": 3},
    )
    assert result["success"] is True
    assert "bar_chart" in result["chart_data"]
    assert "North" in result["answer_template"] or "West" in result["answer_template"]


@pytest.mark.asyncio
async def test_compare_segments_tool(sales_df):
    result = execute_tool(
        sales_df,
        "compare_segments",
        {"segment_column": "region", "metric_column": "revenue"},
    )
    assert result["success"] is True
    assert result["data"]["best_segment"]


@pytest.mark.asyncio
async def test_correlation_tool(regression_df):
    result = execute_tool(regression_df, "correlation_analysis", {"target_column": "profit"})
    assert result["success"] is True
    assert result["data"]["correlations"]


@pytest.mark.asyncio
async def test_anomaly_tool(anomaly_df):
    result = execute_tool(anomaly_df, "anomaly_explanation", {})
    assert result["success"] is True
    assert result["data"]["total_anomalies"] >= 1


@pytest.mark.asyncio
async def test_forecast_tool(sales_df):
    result = execute_tool(
        sales_df,
        "forecast_metric",
        {"target_column": "revenue", "date_column": "date", "horizon": 3},
    )
    assert result["success"] is True
    assert "forecast_chart" in result["chart_data"] or result["data"]["forecast"]


@pytest.mark.asyncio
async def test_model_explanation_tool(regression_df):
    result = execute_tool(regression_df, "model_explanation", {"target_column": "profit"})
    assert result["success"] is True
    assert result["data"]["top_features"]


@pytest.mark.asyncio
async def test_recommendation_tool(sales_df):
    result = execute_tool(sales_df, "generate_business_recommendation", {})
    assert result["success"] is True
    assert result["data"]["recommendations"]


@pytest.mark.asyncio
async def test_invalid_metric_column(sales_df):
    result = execute_tool(
        sales_df,
        "top_n_by_metric",
        {"metric_column": "missing", "group_column": "region"},
    )
    assert result["success"] is False


@pytest.mark.asyncio
async def test_run_agent_top_n_question(sales_df):
    response = await run_agent_chat(sales_df, "Which region has the highest revenue?")
    assert response["tool_used"] == "top_n_by_metric"
    assert response["answer"]
    assert response["confidence"] > 0
    assert response["citations"]


@pytest.mark.asyncio
async def test_run_agent_forecast_question(sales_df):
    response = await run_agent_chat(sales_df, "Forecast next 3 months of revenue")
    assert response["tool_used"] == "forecast_metric"
    assert response["answer"]
    assert response["chart_data"]


@pytest.mark.asyncio
async def test_run_agent_anomaly_question(anomaly_df):
    response = await run_agent_chat(anomaly_df, "Show unusual records")
    assert response["tool_used"] == "anomaly_explanation"
    assert response["citations"]


@pytest.mark.asyncio
async def test_run_agent_shap_question(regression_df):
    response = await run_agent_chat(regression_df, "What variables influence profit most?")
    assert response["tool_used"] == "model_explanation"
    assert response["answer"]


@pytest.mark.asyncio
async def test_run_agent_invalid_forecast_question():
    df = pd.DataFrame({"name": ["a", "b"], "value": [1, 2]})
    response = await run_agent_chat(df, "Forecast next month revenue")
    assert response["tool_used"] == "forecast_metric"
    assert response["confidence"] <= 0.5


@pytest.mark.asyncio
async def test_run_agent_empty_dataset():
    response = await run_agent_chat(pd.DataFrame(), "Summarize this dataset")
    assert response["tool_used"] == "none"
    assert response["confidence"] == 0.0


def test_chat_api_endpoint():
    upload = client.post(
        "/api/upload",
        files={"file": ("sales.csv", SALES_CSV, "text/csv")},
    )
    session_id = upload.json()["session_id"]

    resp = client.post(
        f"/api/sessions/{session_id}/chat",
        json={"question": "Which region has the highest revenue?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"]
    assert data["tool_used"] == "top_n_by_metric"
    assert "bar_chart" in data["chart_data"]
    assert data["confidence"] > 0
    assert data["citations"]


def test_chat_api_empty_question_validation():
    upload = client.post(
        "/api/upload",
        files={"file": ("sales.csv", SALES_CSV, "text/csv")},
    )
    session_id = upload.json()["session_id"]
    resp = client.post(f"/api/sessions/{session_id}/chat", json={"question": ""})
    assert resp.status_code == 422


def test_chat_api_invalid_session():
    resp = client.post(
        "/api/sessions/00000000-0000-0000-0000-000000000000/chat",
        json={"question": "Summarize this dataset"},
    )
    assert resp.status_code == 404


def test_chat_api_summary_question():
    upload = client.post(
        "/api/upload",
        files={"file": ("sales.csv", SALES_CSV, "text/csv")},
    )
    session_id = upload.json()["session_id"]
    resp = client.post(
        f"/api/sessions/{session_id}/chat",
        json={"question": "Summarize this dataset"},
    )
    assert resp.status_code == 200
    assert resp.json()["tool_used"] == "summarize_dataset"
