from typing import Any, Literal

from pydantic import BaseModel, Field


# --- Health ---
class HealthIssue(BaseModel):
    severity: str
    column: str | None = None
    description: str
    recommended_fix: str | None = None


class HealthSubScores(BaseModel):
    completeness: float
    consistency: float
    uniqueness: float
    validity: float
    missing_value_score: float
    duplicate_score: float
    outlier_score: float


class HealthResponse(BaseModel):
    overall_score: float
    sub_scores: HealthSubScores
    issues: list[HealthIssue]
    recommended_fixes: list[str]
    rows: int
    columns: int


# --- Root Cause ---
class RootCauseRequest(BaseModel):
    metric_column: str
    dimension_columns: list[str] | None = None
    period_column: str | None = None
    baseline_label: str | None = None
    comparison_label: str | None = None


class ContributorItem(BaseModel):
    dimension: str
    value: str
    baseline_value: float
    comparison_value: float
    delta: float
    contribution_pct: float


class RootCauseResponse(BaseModel):
    metric_column: str
    metric_change_pct: float
    total_delta: float
    baseline_total: float
    comparison_total: float
    contributors: list[ContributorItem]
    chart_data: dict[str, Any] = Field(default_factory=dict)


# --- Storytelling ---
class StoryResponse(BaseModel):
    what_happened: str
    why_it_happened: str
    what_to_do_next: str
    facts: list[str]
    llm_enhanced: bool = False


# --- Comparison ---
class PeriodCompareRequest(BaseModel):
    metric_column: str | None = None
    date_column: str | None = None
    period: Literal["mom", "qoq", "yoy"] = "mom"


class DatasetCompareRequest(BaseModel):
    session_id_a: str
    session_id_b: str
    metric_columns: list[str] | None = None


class PeriodChangeItem(BaseModel):
    period: str
    previous_period: str
    value: float
    previous_value: float
    change_pct: float
    delta: float


class PeriodCompareResponse(BaseModel):
    metric_column: str
    date_column: str
    period_type: str
    changes: list[PeriodChangeItem]
    summary: str
    emerging_trends: list[str]


class DatasetCompareResponse(BaseModel):
    session_id_a: str
    session_id_b: str
    schema_alignment: dict[str, Any]
    metric_comparisons: list[dict[str, Any]]
    summary: str
    category_shifts: list[dict[str, Any]]


# --- Dashboard ---
class KpiItem(BaseModel):
    label: str
    column: str
    aggregation: str
    value: float
    format: str = "number"


class DashboardPanel(BaseModel):
    id: str
    type: str
    title: str
    config: dict[str, Any]


class DashboardResponse(BaseModel):
    kpis: list[KpiItem]
    panels: list[DashboardPanel]
    quality_alerts: list[str]
    chart_data: dict[str, Any] = Field(default_factory=dict)


# --- Cleaning ---
class CleanRequest(BaseModel):
    instruction: str = Field(min_length=1, max_length=500)
    replace_in_place: bool = False


class CleanAuditItem(BaseModel):
    step: int
    operation: str
    description: str
    rows_before: int
    rows_after: int
    columns_affected: list[str]


class CleanResponse(BaseModel):
    success: bool
    audit_trail: list[CleanAuditItem]
    new_session_id: str | None = None
    rows: int
    columns: int
    preview: list[dict[str, Any]]
    health_score_before: float
    health_score_after: float
    message: str


# --- SQL ---
class SqlRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class SqlResponse(BaseModel):
    sql: str
    explanation: str
    tables_used: list[str]
    columns_referenced: list[str]
    assumptions: list[str]


# --- Report V2 ---
class ReportScqa(BaseModel):
    situation: str
    complication: str
    implication: str
    answer: str


class PrioritizedRecommendation(BaseModel):
    action: str
    priority: str


class ReportV2Response(BaseModel):
    markdown: str
    executive_summary: str
    scqa: ReportScqa | None = None
    key_findings: list[str]
    risks: list[str]
    opportunities: list[str]
    recommendations: list[str]
    prioritized_recommendations: list[PrioritizedRecommendation] = Field(default_factory=list)
    forecast_outlook: str = ""
    llm_enhanced: bool
    format: str = "markdown"


# --- Experiments ---
class ExperimentItem(BaseModel):
    run_id: str
    session_id: str
    model_name: str
    task_type: str
    hyperparameters: dict[str, Any]
    metrics: dict[str, float]
    timestamp: str
    notes: str


class ExperimentsListResponse(BaseModel):
    experiments: list[ExperimentItem]
    count: int


class ExperimentLogRequest(BaseModel):
    model_name: str
    task_type: str
    hyperparameters: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, float] = Field(default_factory=dict)
    notes: str = ""


class FeatureSetResult(BaseModel):
    label: str
    name: str
    features: list[str]
    feature_count: int
    model_name: str
    metrics: dict[str, float]
    score: float
    rank: int | None = None
    is_best: bool = False


class ExperimentLabResponse(BaseModel):
    task_type: str
    target_column: str
    feature_sets: list[FeatureSetResult]
    best_feature_set: str
    summary: str


# --- Sample Datasets ---
class SampleDatasetItem(BaseModel):
    id: str
    name: str
    description: str
    filename: str
    task_hint: str
    rows: int
    columns: int


class SamplesListResponse(BaseModel):
    samples: list[SampleDatasetItem]
    count: int


class SampleLoadResponse(BaseModel):
    session_id: str
    filename: str
    name: str
    rows: int
    columns: list[str]
    preview: list[dict[str, Any]]
    column_types: dict[str, str]


# --- Multi-Agent ---
class AgentFinding(BaseModel):
    role: str
    findings: list[str]
    confidence: float
    citations: list[str]


class TeamAnalysisResponse(BaseModel):
    executive_summary: str
    analyst_section: AgentFinding
    ml_section: AgentFinding
    business_section: AgentFinding
    qa_section: AgentFinding
    combined_recommendations: list[str]
