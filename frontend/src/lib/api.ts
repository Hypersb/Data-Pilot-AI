export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8080";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = body.detail;
    const msg =
      typeof detail === "string"
        ? detail
        : res.status === 404
          ? "Endpoint or session not found. Restart the backend and upload your dataset again."
          : `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return res.json();
}

export async function uploadFile(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: form,
  });
  return handleResponse<import("./types").UploadResponse>(res);
}

export async function getProfile(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/profile`);
  return handleResponse<import("./types").ProfileResponse>(res);
}

export async function getInsights(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/insights`);
  return handleResponse<import("./types").InsightsResponse>(res);
}

export async function getAnomalies(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/anomalies`);
  return handleResponse<import("./types").AnomalyResponse>(res);
}

export async function getForecastLeaderboard(
  sessionId: string,
  params?: { target_column?: string; date_column?: string; forecast_horizon?: number }
) {
  const qs = new URLSearchParams();
  if (params?.target_column) qs.set("target_column", params.target_column);
  if (params?.date_column) qs.set("date_column", params.date_column);
  if (params?.forecast_horizon) qs.set("forecast_horizon", String(params.forecast_horizon));
  const res = await fetch(
    `${API_BASE}/api/sessions/${sessionId}/forecast?${qs.toString()}`
  );
  return handleResponse<import("./types").ForecastLeaderboardResponse>(res);
}

export async function runAutoML(
  sessionId: string,
  body?: { target_column?: string; date_column?: string }
) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/automl`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {}),
  });
  return handleResponse<import("./types").AutoMLResponse>(res);
}

export async function getModelArena(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/models`);
  return handleResponse<import("./types").ModelArenaResponse>(res);
}

export async function getXAI(
  sessionId: string,
  params?: { target_column?: string; row_index?: number }
) {
  const qs = new URLSearchParams();
  if (params?.target_column) qs.set("target_column", params.target_column);
  if (params?.row_index != null) qs.set("row_index", String(params.row_index));
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/xai?${qs.toString()}`);
  return handleResponse<import("./types").XAIResponse>(res);
}

export async function sendChat(sessionId: string, question: string) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return handleResponse<import("./types").ChatResponse>(res);
}

export async function deleteSession(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`, {
    method: "DELETE",
  });
  return handleResponse<{ message: string }>(res);
}

// V3 analysis bundle
export async function getAnalysis(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/analysis`);
  return handleResponse<import("./types").AnalysisResponse>(res);
}

export async function getCharts(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/charts`);
  return handleResponse<import("./types").ChartsResponse>(res);
}

// V2 API
export async function getHealth(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/health`);
  return handleResponse<import("./types").HealthResponse>(res);
}

export async function postRootCause(sessionId: string, body: import("./types").RootCauseRequest) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/root-cause`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse<import("./types").RootCauseResponse>(res);
}

export async function getStory(sessionId: string, topic?: string) {
  const qs = topic ? `?topic=${encodeURIComponent(topic)}` : "";
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/story${qs}`);
  return handleResponse<import("./types").StoryResponse>(res);
}

export async function comparePeriod(sessionId: string, body: import("./types").PeriodCompareRequest) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/compare/period`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse<import("./types").PeriodCompareResponse>(res);
}

export async function compareDatasets(body: import("./types").DatasetCompareRequest) {
  const res = await fetch(`${API_BASE}/api/sessions/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse<import("./types").DatasetCompareResponse>(res);
}

export async function getDashboard(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/dashboard`);
  return handleResponse<import("./types").DashboardResponse>(res);
}

export async function cleanDataset(sessionId: string, body: import("./types").CleanRequest) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/clean`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse<import("./types").CleanResponse>(res);
}

export async function generateSql(sessionId: string, body: import("./types").SqlRequest) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/sql`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse<import("./types").SqlResponse>(res);
}

export async function getReportV2(sessionId: string, format: "markdown" | "pdf" | "pptx" = "markdown") {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/report/v2?format=${format}`);
  if (format === "pdf" || format === "pptx") {
    if (!res.ok) throw new Error(`Request failed (${res.status})`);
    return res.blob();
  }
  return handleResponse<import("./types").ReportV2Response>(res);
}

export async function getExperiments(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/experiments`);
  return handleResponse<import("./types").ExperimentsListResponse>(res);
}

export async function getExperimentLab(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/experiments/lab`);
  return handleResponse<import("./types").ExperimentLabResponse>(res);
}

export async function getSampleDatasets() {
  const res = await fetch(`${API_BASE}/api/samples`);
  return handleResponse<import("./types").SamplesListResponse>(res);
}

export async function loadSampleDataset(sampleId: string) {
  const res = await fetch(`${API_BASE}/api/samples/${sampleId}/load`, { method: "POST" });
  return handleResponse<import("./types").SampleLoadResponse>(res);
}

export async function runTeamAnalysis(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/team-analysis`, {
    method: "POST",
  });
  return handleResponse<import("./types").TeamAnalysisResponse>(res);
}
