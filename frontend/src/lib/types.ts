export interface UploadResponse {
  session_id: string;
  filename: string;
  rows: number;
  columns: string[];
  preview: Record<string, unknown>[];
  column_types: Record<string, string>;
}

export interface ProfileResponse {
  rows: number;
  columns: number;
  duplicate_rows: number;
  missing_cells: number;
  completeness_pct: number;
  quality_score: number;
  quality_flags: string[];
  columns_info: ColumnInfo[];
  column_types: Record<string, string>;
}

export interface ColumnInfo {
  name: string;
  dtype: string;
  null_count: number;
  null_pct: number;
  unique_count: number;
  min?: number;
  max?: number;
  mean?: number;
  std?: number;
  top_values?: { value: string; count: number }[];
}

export interface InsightItem {
  type: string;
  title: string;
  description: string;
  severity: string;
  related_columns: string[];
}

export interface InsightsResponse {
  insights: InsightItem[];
  count: number;
}

export interface AnomalyRowItem {
  row_index: number;
  severity: string;
  methods: string[];
  columns: string[];
  explanation: string;
  values: Record<string, unknown>;
  title?: string;
  date?: string;
  impact_pct?: number;
  possible_causes?: string[];
}

export interface AnomalyResponse {
  available: boolean;
  total_anomalies: number;
  anomaly_methods_used: string[];
  plain_english_explanation: string;
  anomaly_summary: string;
  anomaly_rows?: AnomalyRowItem[];
  top_anomalous_columns?: { column: string; display_name: string; anomaly_count: number }[];
  severity_score?: number;
  chart_data?: { anomaly_chart?: Record<string, unknown> };
}

export interface AutoMLModelEntry {
  model_name: string;
  metrics: Record<string, number>;
  rank: number | null;
  is_best: boolean;
  status: string;
  training_time_ms?: number;
  prediction_time_ms?: number;
  score?: number;
  description?: string;
}

export interface ModelArenaResponse {
  task_type: string;
  target_column: string;
  feature_columns: string[];
  detection_reason: string;
  primary_metric: string;
  leaderboard: AutoMLModelEntry[];
  best_model: {
    model_name: string;
    metrics: Record<string, number>;
    rank: number;
    description?: string;
    why_it_won?: string;
  };
  model_explanation: string;
  performance_summary: string;
  models_trained: number;
}

export interface AutoMLResponse {
  task_type: string;
  target_column: string;
  date_column: string | null;
  best_model: { model_name: string; metrics: Record<string, number> };
  leaderboard: AutoMLModelEntry[];
  models_trained: number;
}

export interface ForecastLeaderboardEntry {
  rank: number;
  model_name: string;
  metrics: Record<string, number>;
  is_best: boolean;
}

export interface ForecastExecutiveSummary {
  current_trend: string;
  trend_pct: number;
  forecast_period_label: string;
  projected_change_pct: number;
  confidence_level: string;
  best_case: number;
  worst_case: number;
  ai_commentary: string;
  plain_english?: string;
}

export interface ForecastLeaderboardResponse {
  target_column: string;
  date_column: string;
  forecast_horizon: number;
  explanation: string;
  leaderboard: ForecastLeaderboardEntry[];
  best_model: ForecastLeaderboardEntry;
  forecast: { date: string; value: number; lower?: number; upper?: number }[];
  chart_data: { forecast_chart?: Record<string, unknown> };
  executive_summary?: ForecastExecutiveSummary;
}

export interface XAIResponse {
  available: boolean;
  model_name: string;
  target_column: string;
  global_explanation: string;
  top_features: {
    rank: number;
    display_name: string;
    importance: number;
    direction: string;
  }[];
  chart_data: { importance_bar?: Record<string, unknown> };
}

export interface ChartsResponse {
  charts: ChartItem[];
  count: number;
}

export interface ChartItem {
  id: string;
  type: string;
  title: string;
  figure: Record<string, unknown>;
}

export interface AnalysisResponse {
  profile: ProfileResponse;
  insights: InsightItem[];
  insight_count: number;
  dashboard: DashboardResponse;
  forecast_available: boolean;
  forecast_message: string;
  forecast: ForecastLeaderboardResponse | null;
}

export interface ChatResponse {
  answer: string;
  tool_used: string;
  confidence: number;
  citations: string[];
  chart_data: Record<string, unknown>;
  follow_up_questions: string[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  tool_used?: string;
  confidence?: number;
  citations?: string[];
  chart_data?: Record<string, unknown>;
}

// V2 types
export interface HealthIssue {
  severity: string;
  column: string | null;
  description: string;
  recommended_fix: string | null;
}

export interface HealthSubScores {
  completeness: number;
  consistency: number;
  uniqueness: number;
  validity: number;
  missing_value_score: number;
  duplicate_score: number;
  outlier_score: number;
}

export interface HealthResponse {
  overall_score: number;
  sub_scores: HealthSubScores;
  issues: HealthIssue[];
  recommended_fixes: string[];
  rows: number;
  columns: number;
}

export interface RootCauseRequest {
  metric_column: string;
  dimension_columns?: string[];
  period_column?: string;
}

export interface ContributorItem {
  dimension: string;
  value: string;
  baseline_value: number;
  comparison_value: number;
  delta: number;
  contribution_pct: number;
}

export interface RootCauseResponse {
  metric_column: string;
  metric_change_pct: number;
  total_delta: number;
  baseline_total: number;
  comparison_total: number;
  contributors: ContributorItem[];
  chart_data: Record<string, unknown>;
}

export interface StoryResponse {
  what_happened: string;
  why_it_happened: string;
  what_to_do_next: string;
  facts: string[];
  llm_enhanced: boolean;
}

export interface PeriodCompareRequest {
  metric_column?: string;
  date_column?: string;
  period?: "mom" | "qoq" | "yoy";
}

export interface PeriodChangeItem {
  period: string;
  previous_period: string;
  value: number;
  previous_value: number;
  change_pct: number;
  delta: number;
}

export interface PeriodCompareResponse {
  metric_column: string;
  date_column: string;
  period_type: string;
  changes: PeriodChangeItem[];
  summary: string;
  emerging_trends: string[];
}

export interface DatasetCompareRequest {
  session_id_a: string;
  session_id_b: string;
  metric_columns?: string[];
}

export interface DatasetCompareResponse {
  session_id_a: string;
  session_id_b: string;
  schema_alignment: Record<string, unknown>;
  metric_comparisons: Record<string, unknown>[];
  summary: string;
  category_shifts: Record<string, unknown>[];
}

export interface KpiItem {
  label: string;
  column: string;
  aggregation: string;
  value: number;
  format: string;
}

export interface DashboardPanel {
  id: string;
  type: string;
  title: string;
  config: Record<string, unknown>;
}

export interface DashboardResponse {
  kpis: KpiItem[];
  panels: DashboardPanel[];
  quality_alerts: string[];
  chart_data: Record<string, unknown>;
}

export interface CleanRequest {
  instruction: string;
  replace_in_place?: boolean;
}

export interface CleanAuditItem {
  step: number;
  operation: string;
  description: string;
  rows_before: number;
  rows_after: number;
  columns_affected: string[];
}

export interface CleanResponse {
  success: boolean;
  audit_trail: CleanAuditItem[];
  new_session_id: string | null;
  rows: number;
  columns: number;
  preview: Record<string, unknown>[];
  health_score_before: number;
  health_score_after: number;
  message: string;
}

export interface SqlRequest {
  question: string;
}

export interface SqlResponse {
  sql: string;
  explanation: string;
  tables_used: string[];
  columns_referenced: string[];
  assumptions: string[];
}

export interface ReportScqa {
  situation: string;
  complication: string;
  implication: string;
  answer: string;
}

export interface PrioritizedRecommendation {
  action: string;
  priority: string;
}

export interface ReportV2Response {
  markdown: string;
  executive_summary: string;
  scqa?: ReportScqa;
  key_findings: string[];
  risks: string[];
  opportunities: string[];
  recommendations: string[];
  prioritized_recommendations?: PrioritizedRecommendation[];
  forecast_outlook?: string;
  llm_enhanced: boolean;
  format: string;
}

export interface ExperimentItem {
  run_id: string;
  session_id: string;
  model_name: string;
  task_type: string;
  hyperparameters: Record<string, unknown>;
  metrics: Record<string, number>;
  timestamp: string;
  notes: string;
}

export interface ExperimentsListResponse {
  experiments: ExperimentItem[];
  count: number;
}

export interface FeatureSetResult {
  label: string;
  name: string;
  features: string[];
  feature_count: number;
  model_name: string;
  metrics: Record<string, number>;
  score: number;
  rank?: number;
  is_best?: boolean;
}

export interface ExperimentLabResponse {
  task_type: string;
  target_column: string;
  feature_sets: FeatureSetResult[];
  best_feature_set: string;
  summary: string;
}

export interface SampleDatasetItem {
  id: string;
  name: string;
  description: string;
  filename: string;
  task_hint: string;
  rows: number;
  columns: number;
}

export interface SamplesListResponse {
  samples: SampleDatasetItem[];
  count: number;
}

export interface SampleLoadResponse {
  session_id: string;
  filename: string;
  name: string;
  rows: number;
  columns: string[];
  preview: Record<string, unknown>[];
  column_types: Record<string, string>;
}

export interface AgentFinding {
  role: string;
  findings: string[];
  confidence: number;
  citations: string[];
}

export interface TeamAnalysisResponse {
  executive_summary: string;
  analyst_section: AgentFinding;
  ml_section: AgentFinding;
  business_section: AgentFinding;
  qa_section: AgentFinding;
  combined_recommendations: string[];
}
