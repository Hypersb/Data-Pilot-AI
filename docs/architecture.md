# Prisma AI — Architecture

## System Overview

Prisma AI is an API-first data analysis platform with a Streamlit dashboard. Users upload CSV or Excel files; the backend profiles the data, runs analytics and ML pipelines, and returns structured JSON responses. The UI consumes the same service layer as the REST API.

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│  Streamlit UI   │────▶│  Service Layer   │◀────│  FastAPI REST API       │
│  (dashboard)    │     │  (Python)        │     │  (/api/sessions/...)    │
└─────────────────┘     └────────┬─────────┘     └─────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              In-memory    Analytics/ML    Ollama (optional)
              SessionStore   Engines         LLM planning & narrative
```

### Components

| Component | Location | Role |
|-----------|----------|------|
| FastAPI app | `backend/app/main.py` | HTTP routing, CORS, health check |
| Routers | `backend/app/routers/` | Upload, profile, insights, charts, forecast, AutoML, XAI, anomalies, chat, report |
| Services | `backend/app/services/` | Business logic — ingest, profiler, insight engine, viz, forecast, AutoML, SHAP, anomalies, agent |
| Schemas | `backend/app/schemas/` | Pydantic request/response models |
| Streamlit UI | `backend/streamlit_app/main.py` | Primary user interface |
| Tests | `backend/tests/` | Pytest suite (73 tests) |

---

## Data Flow

### 1. Upload and session

1. User uploads a file via Streamlit or `POST /api/upload`.
2. `ingest.py` parses CSV/Excel and validates file type.
3. A session ID is created; the DataFrame is stored in an in-memory `SessionStore`.
4. Preview rows and inferred column types are returned.

### 2. Analytics pipeline

After upload, any endpoint can retrieve the session DataFrame and run a service:

```
Upload → SessionStore → Router → Service Engine → Pydantic Response → JSON
```

Example: `GET /api/sessions/{id}/insights` → `insight_engine.generate_insights(df)` → ranked insight list.

### 3. ML pipeline

AutoML, forecasting, and explainability follow the same pattern:

```
DataFrame → task detection → model training / backtesting → leaderboard or metrics → response
```

- **AutoML** detects regression, classification, or forecasting and trains multiple models.
- **Forecasting leaderboard** runs rolling-window backtests across ARIMA, Prophet, lag-based Linear Regression, and XGBoost.
- **XAI (SHAP)** fits the AutoML best model and computes global and local feature importance.

### 4. Agent pipeline

The Natural Language Data Analyst uses a tool-calling pattern:

```
Question → LLM planner (or heuristic fallback) → AgentPlan (Pydantic)
        → Tool execution (grounded service call)
        → Verified facts + chart_data
        → LLM explanation (optional) → ChatResponse
```

The LLM selects tools and explains results. It does not compute statistics itself.

---

## API-First Design

Every major capability is exposed as a REST endpoint under `/api/sessions/{session_id}/...`:

- Routers stay thin — they load the session DataFrame, call a service, and return typed responses.
- Streamlit imports services directly for local development (same logic, no duplicate implementations).
- Pydantic models enforce response shape for clients, tests, and documentation.

This separation makes the backend testable with `TestClient` and deployable independently of the UI.

---

## ML Pipeline Details

### AutoML (`automl_engine.py`)

- Infers task type: regression, classification, or forecasting (datetime + numeric target).
- Trains candidate models (e.g. Linear Regression, Random Forest, XGBoost; ARIMA/Prophet for forecasting).
- Ranks models on held-out metrics and returns a leaderboard with a best model.

### Forecasting leaderboard (`forecast_engine.py`)

- Requires datetime column + numeric target.
- Rolling-window backtesting with MAPE, RMSE, and MAE.
- Best model generates forward forecast with confidence intervals when supported.
- Plotly chart JSON included in the response.

### Explainable AI (`xai_engine.py`)

- Uses the AutoML best tabular model.
- SHAP TreeExplainer or LinearExplainer for feature importance.
- Returns top features, global narrative, local row explanations, and Plotly charts.

### Anomaly detection (`anomaly_engine.py`)

- Combines IQR, modified Z-score, Isolation Forest, and optional time-series rolling z-score.
- Returns flagged rows, severity, methods used, and chart data.

---

## Agent Safety Design

### Problem

Early NLQ systems often let the LLM write and execute Python or SQL against user data. That creates risks:

- Arbitrary code execution
- Hallucinated numbers presented as facts
- Unbounded access to the runtime environment

### Prisma AI approach: tool calling only

The agent (`agent_engine.py` + `agent_tools.py`) is constrained to a fixed registry of eight tools. Each tool:

1. Accepts Pydantic-validated arguments.
2. Calls an existing analytics service (profiler, forecast engine, SHAP, etc.).
3. Returns **verified facts** and optional chart JSON — never free-form computed output from the LLM.

Flow:

```
User question
    ↓
AgentPlan { tool_name, arguments }  ← validated by Pydantic
    ↓
execute_tool() → grounded facts from real data
    ↓
LLM writes explanation using ONLY those facts (or template fallback if Ollama is offline)
```

### Safety guarantees

| Rule | Implementation |
|------|----------------|
| No arbitrary Python | No `eval()`, no exec, no generated dataframe code |
| No self-computed stats by LLM | All numbers come from tool results |
| Strict schemas | `AgentPlan` and per-tool argument models reject invalid payloads |
| Graceful degradation | Failed tools return errors; other models/pipelines continue where applicable |
| Heuristic fallback | Keyword-based planner when Ollama is unavailable — still uses tools only |

### Why this is safer than raw code execution

- **Bounded surface area** — only eight named operations, each auditable.
- **Testable** — every tool has unit tests; agent tests cover selection and API integration.
- **Grounded citations** — responses include fact strings traceable to tool output.
- **Separation of reasoning and computation** — the LLM plans and explains; Python services compute.

---

## Deployment Notes

- **Session storage** is in-memory (no database in the current MVP). Sessions expire after a configurable TTL.
- **Ollama** is optional. Core analytics, ML, and template-based agent answers work without it; LLM-enhanced planning and narratives require a running Ollama instance.
- Docker Compose and `render.yaml` support containerized deployment.

---

## Related Documentation

- [README](../README.md) — setup and API reference
- [Demo script](./demo_script.md) — presentation walkthrough
- [Project evaluation](./project_evaluation.md) — recruiter-facing summary
