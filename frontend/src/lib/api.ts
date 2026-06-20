export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = body.detail;
    throw new Error(
      typeof detail === "string" ? detail : `Request failed (${res.status})`
    );
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
