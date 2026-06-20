# Prisma AI — Project Evaluation

A recruiter- and interviewer-oriented assessment of what this project demonstrates. All claims reflect **implemented** functionality in the current codebase.

---

## Why This Is Stronger Than a Typical Student Project

| Typical student project | Prisma AI |
|-------------------------|-----------|
| Single Jupyter notebook | Modular Python services + REST API + UI |
| One ML model on a fixed dataset | AutoML with task detection + model leaderboard |
| Static matplotlib charts | Plotly charts via API JSON; dashboard tabs |
| “Chat with your data” via prompt + pandas exec | Tool-calling agent with Pydantic validation — no arbitrary code |
| No tests or a few smoke tests | **73 pytest tests** across API, ML, and agent |
| README with install steps only | Architecture docs, demo script, resume bullets |

The project shows **product thinking** (upload → insight → action), **ML engineering** (backtesting, model comparison, SHAP), and **software discipline** (schemas, routers, tests).

---

## ML Concepts Used

| Concept | Where it appears |
|---------|------------------|
| Task type detection | AutoML — regression, classification, forecasting |
| Train/holdout evaluation | AutoML leaderboard; forecast rolling-window backtest |
| Time-series forecasting | ARIMA, Prophet, lag features + Linear Regression, XGBoost |
| Error metrics | MAPE, RMSE, MAE (forecast leaderboard) |
| Ensemble / tree models | Random Forest, XGBoost (AutoML) |
| Anomaly detection | IQR, modified Z-score, Isolation Forest, time-series z-score |
| Explainability | SHAP TreeExplainer / LinearExplainer on best AutoML model |
| Feature importance ranking | Global and local SHAP contributors |
| Model selection | Leaderboards for AutoML and forecasting |

---

## Software Engineering Concepts Used

| Concept | Where it appears |
|---------|------------------|
| API-first design | FastAPI routers; typed Pydantic responses |
| Separation of concerns | Routers vs service engines vs schemas |
| Configuration management | `pydantic-settings` for env vars |
| Session management | In-memory store with TTL |
| Async HTTP | Ollama client for LLM planning/explanation |
| Test-driven quality | pytest + FastAPI TestClient + async agent tests |
| Containerization | Dockerfile, docker-compose, render.yaml |
| Safe agent design | Fixed tool registry; no eval/exec |

---

## What Recruiters Should Notice

### For ML / AIML roles

- You compare **multiple models** and report metrics — not a single hard-coded sklearn call.
- Forecasting uses **backtesting**, not in-sample fit only.
- NL interface is **grounded** — relevant to production ML systems concerns (hallucination, safety).
- **SHAP** integration shows awareness of explainability requirements.

### For Data Analyst roles

- End-to-end workflow from **raw file to narrative**: profile → insights → charts → forecast → report.
- Segment and ranking questions are **automated** via the agent and analytics tools.
- Outputs are **business-readable** (plain English anomalies, executive markdown reports).

### For Software Engineer roles

- **73 tests** — signals maintainability and regression awareness.
- Clean **module boundaries** — easy to describe in system design interviews.
- Optional LLM (Ollama) **does not block** core paths — good degradation story.

---

## Honest Limitations (Worth Mentioning in Interviews)

- **In-memory sessions** — data is not persisted to a database; sessions expire.
- **No authentication** — suitable for MVP/demo, not multi-tenant production.
- **Streamlit + API share services** — Streamlit does not always call HTTP locally (known dual-path pattern).
- **Ollama optional** — agent uses heuristic tool selection and template answers when LLM is offline.
- **Legacy Next.js frontend** in `frontend/` is not the primary UI; Streamlit is the maintained dashboard.

Framing limitations as conscious MVP scope reads better than overselling.

---

## Suggested GitHub README Signals

- Badges: Python, FastAPI, Streamlit, pytest, test count
- Link to `docs/architecture.md` for depth
- Screenshot placeholders for Forecast, AutoML, and AI Data Analyst tabs
- “73 tests passing” in CI or manual test instructions

---

## One-Sentence Pitch

**Prisma AI is a tested, API-first Python platform that turns spreadsheet uploads into profiles, ML leaderboards, SHAP explanations, forecasts, and grounded natural-language answers — without letting the LLM execute code or invent statistics.**
