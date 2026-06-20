from typing import Any

from app.schemas.agent import ChatResponse
from app.services.agent_engine import run_agent_chat


async def answer_query(df, question: str) -> dict[str, Any]:
    """Backward-compatible NLQ entrypoint backed by the tool agent."""
    result = await run_agent_chat(df, question)
    response = ChatResponse(**result)
    chart = None
    if response.chart_data.get("bar_chart"):
        chart = response.chart_data["bar_chart"]
    elif response.chart_data.get("forecast_chart"):
        chart = response.chart_data["forecast_chart"]
    elif response.chart_data.get("anomaly_chart"):
        chart = response.chart_data["anomaly_chart"]
    elif response.chart_data.get("importance_bar"):
        chart = response.chart_data["importance_bar"]

    return {
        "answer": response.answer,
        "intent": response.tool_used,
        "chart": chart,
        "tool_used": response.tool_used,
        "confidence": response.confidence,
        "citations": response.citations,
        "chart_data": response.chart_data,
        "follow_up_questions": response.follow_up_questions,
    }
