export class SessionExpiredError extends Error {
  constructor(message = "Session expired or not found.") {
    super(message);
    this.name = "SessionExpiredError";
  }
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function resolveApiBase(): string {
  const url = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (url) return url.replace(/\/$/, "");
  if (process.env.NODE_ENV === "production") {
    throw new Error(
      "NEXT_PUBLIC_API_URL is required in production. Set it in Vercel environment variables.",
    );
  }
  return "http://127.0.0.1:8080";
}

export const API_BASE = resolveApiBase();

async function handleResponse<T>(res: Response, sessionScoped = false): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = body.detail;
    const msg =
      typeof detail === "string"
        ? detail
        : res.status === 404 && sessionScoped
          ? "Session expired or not found."
          : res.status === 404
            ? "Endpoint or session not found. Restart the backend and upload your dataset again."
            : `Request failed (${res.status})`;
    if (res.status === 404 && sessionScoped) {
      throw new SessionExpiredError(msg);
    }
    throw new ApiError(msg, res.status);
  }
  return res.json();
}

function sessionUrl(sessionId: string, path: string) {
  return `${API_BASE}/api/sessions/${sessionId}${path}`;
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
  const res = await fetch(sessionUrl(sessionId, "/profile"));
  return handleResponse<import("./types").ProfileResponse>(res, true);
}

export async function getInsights(sessionId: string) {
  const res = await fetch(sessionUrl(sessionId, "/insights"));
  return handleResponse<import("./types").InsightsResponse>(res, true);
}

export async function getAnomalies(sessionId: string) {
  const res = await fetch(sessionUrl(sessionId, "/anomalies"));
  return handleResponse<import("./types").AnomalyResponse>(res, true);
}

export async function getForecastLeaderboard(
  sessionId: string,
  params?: { target_column?: string; date_column?: string; forecast_horizon?: number }
) {
  const qs = new URLSearchParams();
  if (params?.target_column) qs.set("target_column", params.target_column);
  if (params?.date_column) qs.set("date_column", params.date_column);
  if (params?.forecast_horizon) qs.set("forecast_horizon", String(params.forecast_horizon));
  const res = await fetch(`${sessionUrl(sessionId, "/forecast")}?${qs.toString()}`);
  return handleResponse<import("./types").ForecastLeaderboardResponse>(res, true);
}

export async function runAutoML(
  sessionId: string,
  body?: { target_column?: string; date_column?: string }
) {
  const res = await fetch(sessionUrl(sessionId, "/automl"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {}),
  });
  return handleResponse<import("./types").AutoMLResponse>(res, true);
}

export async function getModelArena(sessionId: string) {
  const res = await fetch(sessionUrl(sessionId, "/models"));
  return handleResponse<import("./types").ModelArenaResponse>(res, true);
}

export async function getXAI(
  sessionId: string,
  params?: { target_column?: string; row_index?: number }
) {
  const qs = new URLSearchParams();
  if (params?.target_column) qs.set("target_column", params.target_column);
  if (params?.row_index != null) qs.set("row_index", String(params.row_index));
  const res = await fetch(`${sessionUrl(sessionId, "/xai")}?${qs.toString()}`);
  return handleResponse<import("./types").XAIResponse>(res, true);
}

export async function sendChat(
  sessionId: string,
  question: string,
  history?: Array<{ role: string; content: string }>
) {
  const res = await fetch(sessionUrl(sessionId, "/chat"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history }),
  });
  return handleResponse<import("./types").ChatResponse>(res, true);
}

export async function deleteSession(sessionId: string) {
  const res = await fetch(sessionUrl(sessionId, ""), {
    method: "DELETE",
  });
  return handleResponse<{ message: string }>(res, true);
}

export async function getAnalysis(sessionId: string) {
  const res = await fetch(sessionUrl(sessionId, "/analysis"));
  return handleResponse<import("./types").AnalysisResponse>(res, true);
}

export async function getCharts(sessionId: string) {
  const res = await fetch(sessionUrl(sessionId, "/charts"));
  return handleResponse<import("./types").ChartsResponse>(res, true);
}

export async function getHealth(sessionId: string) {
  const res = await fetch(sessionUrl(sessionId, "/health"));
  return handleResponse<import("./types").HealthResponse>(res, true);
}

export async function postRootCause(sessionId: string, body: import("./types").RootCauseRequest) {
  const res = await fetch(sessionUrl(sessionId, "/root-cause"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse<import("./types").RootCauseResponse>(res, true);
}

export async function getStory(sessionId: string, topic?: string) {
  const qs = topic ? `?topic=${encodeURIComponent(topic)}` : "";
  const res = await fetch(`${sessionUrl(sessionId, "/story")}${qs}`);
  return handleResponse<import("./types").StoryResponse>(res, true);
}

export async function comparePeriod(sessionId: string, body: import("./types").PeriodCompareRequest) {
  const res = await fetch(sessionUrl(sessionId, "/compare/period"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse<import("./types").PeriodCompareResponse>(res, true);
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
  const res = await fetch(sessionUrl(sessionId, "/dashboard"));
  return handleResponse<import("./types").DashboardResponse>(res, true);
}

export async function cleanDataset(sessionId: string, body: import("./types").CleanRequest) {
  const res = await fetch(sessionUrl(sessionId, "/clean"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse<import("./types").CleanResponse>(res, true);
}

export async function generateSql(sessionId: string, body: import("./types").SqlRequest) {
  const res = await fetch(sessionUrl(sessionId, "/sql"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse<import("./types").SqlResponse>(res, true);
}

export async function getReportV2(sessionId: string, format: "markdown" | "pdf" | "pptx" = "markdown") {
  const res = await fetch(`${sessionUrl(sessionId, "/report/v2")}?format=${format}`);
  if (format === "pdf" || format === "pptx") {
    if (!res.ok) {
      if (res.status === 404) throw new SessionExpiredError();
      throw new ApiError(`Request failed (${res.status})`, res.status);
    }
    return res.blob();
  }
  return handleResponse<import("./types").ReportV2Response>(res, true);
}

export async function getExperiments(sessionId: string) {
  const res = await fetch(sessionUrl(sessionId, "/experiments"));
  return handleResponse<import("./types").ExperimentsListResponse>(res, true);
}

export async function getExperimentLab(sessionId: string) {
  const res = await fetch(sessionUrl(sessionId, "/experiments/lab"));
  return handleResponse<import("./types").ExperimentLabResponse>(res, true);
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
  const res = await fetch(sessionUrl(sessionId, "/team-analysis"), {
    method: "POST",
  });
  return handleResponse<import("./types").TeamAnalysisResponse>(res, true);
}

export function isSessionExpiredError(error: unknown): error is SessionExpiredError {
  return error instanceof SessionExpiredError;
}
