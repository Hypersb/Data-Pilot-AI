from __future__ import annotations

import json
from typing import Any

import pandas as pd

from app.schemas.agent import TOOL_ARGUMENT_MODELS, VALID_TOOLS, AgentPlan, ChatResponse
from app.services.agent_tools import execute_tool
from app.services.ingest import infer_column_types
from app.services.llm import generate_text, llm_is_enabled
from app.services.profiler import profile_dataframe

TOOL_DESCRIPTIONS = """
- summarize_dataset: Overview of rows, columns, quality, and schema.
- top_n_by_metric: Rank categories by a numeric metric (highest/lowest).
- compare_segments: Compare average performance across segments.
- correlation_analysis: Show which variables correlate with a target metric.
- anomaly_explanation: Explain unusual records and outliers.
- forecast_metric: Forecast a numeric metric over future periods.
- model_explanation: SHAP-based feature importance for a target.
- generate_business_recommendation: Actionable recommendations from insights.
""".strip()

QUESTION_TOOL_HINTS: list[tuple[str, tuple[str, ...]]] = [
    ("forecast_metric", ("forecast", "predict", "future", "next month", "next quarter")),
    ("anomaly_explanation", ("anomaly", "anomalies", "unusual", "outlier", "abnormal")),
    (
        "model_explanation",
        ("influence", "shap", "feature importance", "variables influence", "what drives", "what variables"),
    ),
    ("compare_segments", ("compare", "segment", "versus", " vs ", "difference between", "perform best", "customer segment", "which segment")),
    ("top_n_by_metric", ("top", "highest", "most", "best", "leading", "which state", "which region", "which product")),
    ("correlation_analysis", ("correlation", "correlate", "related to", "relationship")),
    (
        "generate_business_recommendation",
        ("recommend", "recommendation", "should we", "strategy", "action", "caused", "drop", "decline", "decrease"),
    ),
    ("summarize_dataset", ("summarize", "summary", "overview", "describe")),
]

FOLLOW_UPS: dict[str, list[str]] = {
    "summarize_dataset": [
        "Which segment has the highest revenue?",
        "Show me unusual records.",
        "What variables influence profit most?",
    ],
    "top_n_by_metric": [
        "Compare performance across all segments.",
        "Forecast next month's revenue.",
    ],
    "compare_segments": [
        "Which segment should we prioritize?",
        "Show correlation drivers for revenue.",
    ],
    "correlation_analysis": [
        "Explain the model drivers for this target.",
        "Generate business recommendations.",
    ],
    "anomaly_explanation": [
        "What caused the anomaly pattern?",
        "Summarize this dataset.",
    ],
    "forecast_metric": [
        "Which model performed best?",
        "Compare segment performance.",
    ],
    "model_explanation": [
        "Generate business recommendations.",
        "Show unusual records.",
    ],
    "generate_business_recommendation": [
        "Forecast next month's revenue.",
        "Which region performs best?",
    ],
}


async def run_agent_chat(
    df: pd.DataFrame,
    question: str,
    chat_history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    if df.empty:
        return ChatResponse(
            answer="No data is loaded. Upload a dataset before asking questions.",
            tool_used="none",
            confidence=0.0,
            citations=[],
            chart_data={},
            follow_up_questions=["Summarize this dataset."],
        ).model_dump()

    plan = await plan_tool(df, question, chat_history)
    tool_result = execute_tool(df, plan.tool_name, plan.arguments)
    answer, explain_llm = await explain_tool_result(question, tool_result, plan.tool_name)
    follow_ups = FOLLOW_UPS.get(plan.tool_name, FOLLOW_UPS["summarize_dataset"])

    return ChatResponse(
        answer=answer,
        tool_used=plan.tool_name,
        confidence=float(tool_result.get("confidence", 0.5)),
        citations=list(tool_result.get("facts", [])),
        chart_data=dict(tool_result.get("chart_data", {})),
        follow_up_questions=follow_ups,
        llm_enhanced=explain_llm,
    ).model_dump()


async def plan_tool(
    df: pd.DataFrame,
    question: str,
    chat_history: list[dict[str, str]] | None = None,
) -> AgentPlan:
    llm_plan = await _plan_with_llm(df, question, chat_history)
    if llm_plan is not None:
        try:
            return AgentPlan(**llm_plan)
        except ValueError:
            pass
    return heuristic_plan(question, df)


def heuristic_plan(question: str, df: pd.DataFrame) -> AgentPlan:
    lowered = question.lower()
    for tool_name, keywords in QUESTION_TOOL_HINTS:
        if any(keyword in lowered for keyword in keywords):
            return AgentPlan(
                tool_name=tool_name,  # type: ignore[arg-type]
                arguments=_default_arguments(tool_name, df, question),
            )
    return AgentPlan(
        tool_name="summarize_dataset",
        arguments=_default_arguments("summarize_dataset", df, question),
    )


def _default_arguments(tool_name: str, df: pd.DataFrame, question: str) -> dict[str, Any]:
    types = infer_column_types(df)
    numeric = [c for c, t in types.items() if t == "numeric"]
    categorical = [c for c, t in types.items() if t == "categorical"]
    datetime_cols = [c for c, t in types.items() if t == "datetime"]

    args: dict[str, Any] = {}
    if tool_name == "top_n_by_metric":
        args["metric_column"] = _pick_default(numeric, ("revenue", "sales", "profit"))
        args["group_column"] = _pick_default(categorical, ("region", "state", "segment", "product"))
        args["n"] = _extract_horizon_from_question(question, default=5, upper=20)
        args["ascending"] = any(word in question.lower() for word in ("lowest", "worst", "bottom", "least"))
    elif tool_name == "compare_segments":
        args["segment_column"] = _pick_default(categorical, ("segment", "region", "customer"))
        args["metric_column"] = _pick_default(numeric, ("revenue", "sales", "profit"))
    elif tool_name == "correlation_analysis":
        args["target_column"] = _pick_default(numeric, ("profit", "revenue", "sales"))
    elif tool_name == "forecast_metric":
        args["target_column"] = _pick_default(numeric, ("revenue", "sales"))
        args["date_column"] = _pick_default(datetime_cols, ("date",))
        args["horizon"] = _extract_horizon_from_question(question, default=6, upper=24)
    elif tool_name == "model_explanation":
        args["target_column"] = _pick_default(numeric, ("profit", "revenue", "sales"))
        if datetime_cols:
            args["date_column"] = datetime_cols[0]
    elif tool_name == "generate_business_recommendation":
        args["focus_area"] = question if len(question.split()) <= 8 else None
    return args


def _pick_default(columns: list[str], keywords: tuple[str, ...]) -> str | None:
    if not columns:
        return None
    for keyword in keywords:
        for col in columns:
            if keyword in col.lower():
                return col
    return columns[0]


def _extract_horizon_from_question(question: str, default: int, upper: int) -> int:
    tokens = question.replace(",", " ").split()
    for idx, token in enumerate(tokens):
        if token.isdigit():
            value = int(token)
            if 1 <= value <= upper:
                return value
        if token in {"month", "months", "period", "periods"} and idx > 0:
            prev = tokens[idx - 1]
            if prev.isdigit():
                value = int(prev)
                if 1 <= value <= upper:
                    return value
    return default


def _build_context(df: pd.DataFrame) -> str:
    profile = profile_dataframe(df)
    column_types = infer_column_types(df)
    return json.dumps(
        {
            "rows": profile["rows"],
            "columns": list(df.columns),
            "column_types": column_types,
            "quality_score": profile["quality_score"],
        },
        default=str,
    )


async def _plan_with_llm(
    df: pd.DataFrame,
    question: str,
    chat_history: list[dict[str, str]] | None = None,
) -> dict[str, Any] | None:
    if not llm_is_enabled():
        return None
    history_text = ""
    if chat_history:
        recent = chat_history[-4:]
        history_text = "\n".join(f"{m['role']}: {m['content']}" for m in recent)

    prompt = f"""You are a data analyst agent planner for Prisma AI.
Select exactly ONE tool and valid JSON arguments. Do NOT compute answers yourself.

Tools:
{TOOL_DESCRIPTIONS}

Valid tool_name values: {", ".join(VALID_TOOLS)}

Argument schemas:
- summarize_dataset: {{}}
- top_n_by_metric: {{"metric_column": str|null, "group_column": str|null, "n": int, "ascending": bool}}
- compare_segments: {{"segment_column": str|null, "metric_column": str|null}}
- correlation_analysis: {{"target_column": str|null}}
- anomaly_explanation: {{}}
- forecast_metric: {{"target_column": str|null, "date_column": str|null, "horizon": int}}
- model_explanation: {{"target_column": str|null, "date_column": str|null}}
- generate_business_recommendation: {{"focus_area": str|null}}

Dataset context: {_build_context(df)}
Recent chat:
{history_text or "None"}

Question: {question}

Respond with JSON only:
{{"tool_name": "...", "arguments": {{...}}}}"""

    response = await generate_text(prompt)
    if not response:
        return None
    return _parse_json_object(response)


async def explain_tool_result(
    question: str,
    tool_result: dict[str, Any],
    tool_name: str,
) -> tuple[str, bool]:
    if not tool_result.get("success", False):
        return (
            str(tool_result.get("answer_template") or tool_result.get("error") or "Unable to answer."),
            False,
        )

    facts = tool_result.get("facts", [])
    facts_text = "\n".join(f"- {fact}" for fact in facts)
    prompt = f"""You are a grounded data analyst for Prisma AI.
Explain the answer using ONLY the verified tool facts below.
Do NOT invent numbers, columns, or statistics.
Keep the answer to 2-4 sentences.

Question: {question}
Tool used: {tool_name}
Verified facts:
{facts_text}

Write the final user-facing answer:"""

    llm_answer = await generate_text(prompt)
    if llm_answer:
        return llm_answer, True
    return str(tool_result.get("answer_template") or " ".join(facts)), False


def _parse_json_object(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if text.startswith("```"):
        lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
        text = "\n".join(lines).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        payload = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict) or "tool_name" not in payload:
        return None
    tool_name = payload["tool_name"]
    if tool_name not in VALID_TOOLS:
        return None
    arguments = payload.get("arguments", {})
    if not isinstance(arguments, dict):
        return None
    args_model = TOOL_ARGUMENT_MODELS[tool_name]
    args_model(**arguments)
    return {"tool_name": tool_name, "arguments": arguments}


def validate_agent_plan(payload: dict[str, Any]) -> AgentPlan:
    return AgentPlan(**payload)
