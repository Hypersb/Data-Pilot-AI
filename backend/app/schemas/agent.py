from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

ToolName = Literal[
    "summarize_dataset",
    "top_n_by_metric",
    "compare_segments",
    "correlation_analysis",
    "anomaly_explanation",
    "forecast_metric",
    "model_explanation",
    "generate_business_recommendation",
]

VALID_TOOLS: tuple[str, ...] = (
    "summarize_dataset",
    "top_n_by_metric",
    "compare_segments",
    "correlation_analysis",
    "anomaly_explanation",
    "forecast_metric",
    "model_explanation",
    "generate_business_recommendation",
)


class SummarizeDatasetArgs(BaseModel):
    pass


class TopNByMetricArgs(BaseModel):
    metric_column: str | None = None
    group_column: str | None = None
    n: int = Field(default=5, ge=1, le=20)
    ascending: bool = False


class CompareSegmentsArgs(BaseModel):
    segment_column: str | None = None
    metric_column: str | None = None


class CorrelationAnalysisArgs(BaseModel):
    target_column: str | None = None


class AnomalyExplanationArgs(BaseModel):
    pass


class ForecastMetricArgs(BaseModel):
    target_column: str | None = None
    date_column: str | None = None
    horizon: int = Field(default=6, ge=1, le=24)


class ModelExplanationArgs(BaseModel):
    target_column: str | None = None
    date_column: str | None = None


class GenerateBusinessRecommendationArgs(BaseModel):
    focus_area: str | None = None


TOOL_ARGUMENT_MODELS: dict[str, type[BaseModel]] = {
    "summarize_dataset": SummarizeDatasetArgs,
    "top_n_by_metric": TopNByMetricArgs,
    "compare_segments": CompareSegmentsArgs,
    "correlation_analysis": CorrelationAnalysisArgs,
    "anomaly_explanation": AnomalyExplanationArgs,
    "forecast_metric": ForecastMetricArgs,
    "model_explanation": ModelExplanationArgs,
    "generate_business_recommendation": GenerateBusinessRecommendationArgs,
}


class AgentPlan(BaseModel):
    tool_name: ToolName
    arguments: dict[str, Any] = Field(default_factory=dict)

    @field_validator("tool_name", mode="before")
    @classmethod
    def normalize_tool_name(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("tool_name must be a string.")
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "summarize": "summarize_dataset",
            "top_n": "top_n_by_metric",
            "compare": "compare_segments",
            "correlation": "correlation_analysis",
            "anomaly": "anomaly_explanation",
            "forecast": "forecast_metric",
            "model": "model_explanation",
            "recommendation": "generate_business_recommendation",
            "business_recommendation": "generate_business_recommendation",
        }
        return aliases.get(normalized, normalized)

    @model_validator(mode="after")
    def validate_arguments(self) -> "AgentPlan":
        args_model = TOOL_ARGUMENT_MODELS.get(self.tool_name)
        if args_model is None:
            raise ValueError(f"Unknown tool: {self.tool_name}")
        validated = args_model(**self.arguments)
        self.arguments = validated.model_dump()
        return self


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    answer: str
    tool_used: str
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[str] = Field(default_factory=list)
    chart_data: dict[str, Any] = Field(default_factory=dict)
    follow_up_questions: list[str] = Field(default_factory=list)
    llm_enhanced: bool = False
