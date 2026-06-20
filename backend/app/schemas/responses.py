from typing import Any

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    session_id: str
    filename: str
    rows: int
    columns: list[str]
    preview: list[dict[str, Any]]
    column_types: dict[str, str]


class ProfileResponse(BaseModel):
    rows: int
    columns: int
    duplicate_rows: int
    missing_cells: int
    completeness_pct: float
    quality_score: float
    quality_flags: list[str]
    columns_info: list[dict[str, Any]]
    column_types: dict[str, str]


class InsightItem(BaseModel):
    type: str
    title: str
    description: str
    severity: str
    related_columns: list[str]


class InsightsResponse(BaseModel):
    insights: list[InsightItem]
    count: int


class ChartItem(BaseModel):
    id: str
    type: str
    title: str
    figure: dict[str, Any]


class ChartsResponse(BaseModel):
    charts: list[ChartItem]
    count: int


class ForecastRequest(BaseModel):
    target_column: str | None = None
    date_column: str | None = None
    periods: int = Field(default=6, ge=1, le=24)


class ForecastPoint(BaseModel):
    date: str
    value: float
    lower: float | None = None
    upper: float | None = None


class ForecastResponse(BaseModel):
    target_column: str
    date_column: str
    periods: int
    model_used: str
    metrics: dict[str, float]
    historical: list[dict[str, Any]]
    forecast: list[ForecastPoint]


class ForecastLeaderboardEntry(BaseModel):
    rank: int
    model_name: str
    metrics: dict[str, float]
    is_best: bool = False
    status: str = "success"


class ForecastLeaderboardResponse(BaseModel):
    available: bool = True
    target_column: str
    date_column: str
    forecast_horizon: int
    leaderboard: list[ForecastLeaderboardEntry]
    best_model: ForecastLeaderboardEntry
    explanation: str
    historical: list[dict[str, Any]]
    forecast: list[ForecastPoint]
    chart_data: dict[str, Any]


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class QueryResponse(BaseModel):
    answer: str
    intent: str
    chart: dict[str, Any] | None = None
    forecast: dict[str, Any] | None = None
    tool_used: str | None = None
    confidence: float | None = None
    citations: list[str] = Field(default_factory=list)
    chart_data: dict[str, Any] = Field(default_factory=dict)
    follow_up_questions: list[str] = Field(default_factory=list)


class ReportResponse(BaseModel):
    markdown: str
    llm_enhanced: bool


class MessageResponse(BaseModel):
    message: str


class AutoMLRequest(BaseModel):
    target_column: str | None = None
    date_column: str | None = None


class AutoMLModelEntry(BaseModel):
    model_name: str
    metrics: dict[str, float]
    rank: int | None = None
    is_best: bool = False
    status: str = "success"
    error: str | None = None


class AutoMLBestModel(BaseModel):
    model_name: str
    metrics: dict[str, float]
    rank: int


class AutoMLResponse(BaseModel):
    task_type: str
    target_column: str
    date_column: str | None
    feature_columns: list[str]
    detection_reason: str
    leaderboard: list[AutoMLModelEntry]
    best_model: AutoMLBestModel
    models_trained: int


class FeatureImportanceItem(BaseModel):
    feature: str
    display_name: str
    importance: float
    direction: str
    mean_shap_value: float
    rank: int


class LocalContributor(BaseModel):
    feature: str
    display_name: str
    shap_value: float
    feature_value: float | str


class LocalExplanationItem(BaseModel):
    row_index: int
    prediction: float | str
    top_contributors: list[LocalContributor]
    narrative: str


class XAIResponse(BaseModel):
    available: bool = True
    model_name: str
    task_type: str
    target_column: str
    top_features: list[FeatureImportanceItem]
    global_explanation: str
    local_explanations: list[LocalExplanationItem]
    chart_data: dict[str, Any]


class AnomalyRowItem(BaseModel):
    row_index: int
    severity: str
    methods: list[str]
    columns: list[str]
    explanation: str
    values: dict[str, Any]


class TopAnomalousColumn(BaseModel):
    column: str
    display_name: str
    anomaly_count: int
    methods: list[str]


class AnomalyResponse(BaseModel):
    available: bool = True
    total_anomalies: int
    anomaly_methods_used: list[str]
    anomaly_rows: list[AnomalyRowItem]
    anomaly_summary: str
    top_anomalous_columns: list[TopAnomalousColumn]
    severity_score: float
    plain_english_explanation: str
    chart_data: dict[str, Any]
