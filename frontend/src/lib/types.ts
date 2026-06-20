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

export interface AnomalyResponse {
  available: boolean;
  total_anomalies: number;
  anomaly_methods_used: string[];
  plain_english_explanation: string;
  anomaly_summary: string;
}

export interface AutoMLModelEntry {
  model_name: string;
  metrics: Record<string, number>;
  rank: number | null;
  is_best: boolean;
  status: string;
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

export interface ForecastLeaderboardResponse {
  target_column: string;
  date_column: string;
  forecast_horizon: number;
  explanation: string;
  leaderboard: ForecastLeaderboardEntry[];
  best_model: ForecastLeaderboardEntry;
  forecast: { date: string; value: number; lower?: number; upper?: number }[];
  chart_data: { forecast_chart?: Record<string, unknown> };
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
