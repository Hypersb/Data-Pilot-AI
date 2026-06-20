# Prisma AI — Demo Script

Use `sample-data/sales.csv` unless noted. Have Streamlit running: `streamlit run streamlit_app/main.py`.

---

## 2-Minute Demo (Recruiter / Non-Technical)

**[0:00 – 0:20] Hook**

> “Most business teams have spreadsheets but not time to build notebooks, train models, and write reports. **Prisma AI** is a Python copilot: upload a file, ask questions in English, and get grounded answers with charts.”

**[0:20 – 0:50] Upload + Overview**

1. Upload `sample-data/sales.csv`.
2. Open **Overview** — point out row count, column types, quality score.
3. Open **Insights** — scroll one or two auto-generated findings (correlation, trend, category performance).

**[0:50 – 1:30] Two wow moments**

1. **Forecast tab** — run forecast leaderboard. Say:
   > “It backtests ARIMA, Prophet, and XGBoost, ranks them by error metrics, and forecasts the next periods with the winner.”

2. **AI Data Analyst tab** — ask: *“Which region generated the most revenue?”*
   > “The agent picks a tool, runs the aggregation on real data, and returns an answer with sources — it doesn’t make up numbers.”

**[1:30 – 2:00] Close**

> “Under the hood: FastAPI, scikit-learn, SHAP, 73 tests. Everything is API-accessible, so the same logic powers the UI and integrations. Happy to walk through architecture or tests.”

---

## 5-Minute Technical Demo (Engineering / ML Interview)

**[0:00 – 0:45] Problem + architecture**

> “Prisma AI is API-first: upload creates a session, routers call service engines, Pydantic validates responses. Streamlit is one client; FastAPI is the contract.”

Show project tree briefly: `backend/app/routers/`, `backend/app/services/`, `backend/tests/`.

**[0:45 – 1:30] Data ingest and profiling**

1. Upload CSV via UI or mention `POST /api/upload`.
2. **Overview** + `GET /profile` — explain inferred column types and quality score.

**[1:30 – 2:30] Analytics + visualization**

1. **Insights** — rule-based engine (correlations, outliers, trends).
2. **Charts** — Plotly JSON from `viz_engine`.
3. Optional: open http://localhost:8000/docs and show `/insights`, `/charts`.

**[2:30 – 3:30] ML pipelines**

1. **AutoML tab** — task detection (regression vs forecasting), leaderboard, best model.
2. **Explainable AI tab** — SHAP top features on best tabular model.
3. **Anomalies tab** — IQR, Z-score, Isolation Forest; show flagged row.
4. **Forecast tab** — rolling backtest, MAPE/RMSE/MAE table, best model forecast chart.

**[3:30 – 4:30] Agent (differentiator)**

1. **AI Data Analyst** — ask:
   - “Which region has the highest revenue?” → `top_n_by_metric`
   - “Forecast next month’s revenue” → `forecast_metric`
   - “What variables influence profit most?” → `model_explanation` (use a dataset with clear features if needed)

2. Expand **Sources** — cite grounded facts.

> “The LLM only plans and explains. Computation goes through eight registered tools with Pydantic validation — no eval, no arbitrary Python.”

**[4:30 – 5:00] Quality + limitations**

1. Mention **73 pytest tests** — `pytest tests/ -v`.
2. **Report tab** — markdown executive summary.
3. Honest limits: in-memory sessions, no auth, Ollama optional for LLM polish.

---

## Interview Explanation Script (~60 seconds)

> “I built Prisma AI because uploading a CSV shouldn’t require a data scientist in the loop for every question.
>
> The architecture is a FastAPI backend with modular engines: profiling, insights, AutoML, a forecasting leaderboard that backtests ARIMA, Prophet, and XGBoost, SHAP explainability, and multi-method anomaly detection.
>
> For natural language, I used a tool-calling agent — the model selects one of eight tools, arguments are validated with Pydantic, and answers are built from tool output so we don’t hallucinate metrics or execute user code.
>
> The Streamlit UI is the main frontend, but every feature is also a REST endpoint. I have 73 automated tests covering the API, ML engines, and agent routing.
>
> It’s an MVP: sessions are in-memory, there’s no auth yet, and Ollama is optional for LLM narratives — but the analytics and ML paths work standalone.”

---

## Suggested Live Q&A Prep

| Question | Short answer |
|----------|--------------|
| How do you prevent the LLM from hallucinating numbers? | Tool calling only; answers cite facts from service output. |
| How do you pick the best forecast model? | Rolling-window backtest; rank by MAPE; forecast with winner. |
| Why FastAPI + Streamlit? | API-first for testing and integrations; Streamlit for fast demo UI. |
| Biggest limitation? | In-memory sessions — production would need persistent storage and auth. |
| What would you add next? | Database-backed sessions, auth, and cached ML artifacts per session. |
