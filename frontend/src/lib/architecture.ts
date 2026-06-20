export const architectureNodes = [
  {
    id: "user",
    label: "User",
    description: "Uploads CSV or Excel and asks questions in plain English.",
  },
  {
    id: "client",
    label: "Streamlit / Next.js",
    description: "Client surfaces: Streamlit dashboard or this Next.js app. Both call the same backend services.",
  },
  {
    id: "api",
    label: "FastAPI",
    description: "REST API with typed Pydantic responses. Routers stay thin; logic lives in service engines.",
    route: "GET /docs",
  },
  {
    id: "session",
    label: "Session Store",
    description: "In-memory DataFrame storage keyed by session_id. TTL configurable via SESSION_TTL_SECONDS.",
    route: "POST /api/upload",
  },
  {
    id: "engines",
    label: "ML Engines",
    description: "AutoML, Forecast, SHAP, Anomaly, Insight, and Viz engines read session data and return JSON.",
  },
  {
    id: "agent",
    label: "AI Analyst Agent",
    description: "Tool-calling agent with Pydantic validation. Eight registered tools; no arbitrary code execution.",
    route: "POST /api/sessions/{id}/chat",
  },
  {
    id: "ollama",
    label: "Ollama",
    description: "Optional local LLM for agent planning and report narratives. Core analytics work without it.",
    optional: true,
  },
] as const;

export const capabilities = [
  { id: "automl", title: "AutoML", detail: "Regression, classification, forecasting detection" },
  { id: "forecast", title: "Forecast", detail: "ARIMA, Prophet, XGBoost leaderboard" },
  { id: "shap", title: "SHAP", detail: "Global and local feature importance" },
  { id: "anomaly", title: "Anomalies", detail: "IQR, Z-score, Isolation Forest" },
  { id: "agent", title: "Agent", detail: "Grounded tool-calling analyst" },
] as const;

export const storySteps = [
  {
    step: "01",
    title: "Upload",
    body: "Drop a CSV or Excel file. Prisma parses columns, infers types, and creates a session.",
  },
  {
    step: "02",
    title: "Profile",
    body: "Quality score, completeness, and schema summary — no manual EDA notebooks.",
  },
  {
    step: "03",
    title: "Model",
    body: "AutoML and forecasting leaderboards backtest models and rank by held-out metrics.",
  },
  {
    step: "04",
    title: "Ask",
    body: "The AI Analyst selects a tool, runs it on your data, and returns cited answers.",
  },
] as const;
