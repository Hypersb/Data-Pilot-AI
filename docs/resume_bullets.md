# Prisma AI — Resume Bullets

Use these as starting points. Adjust metrics and wording to match your role and resume style.

---

## Short Bullets (1 line each)

- Built **Prisma AI**, a Python data copilot that profiles CSV/Excel uploads and returns insights, forecasts, and ML results via FastAPI and Streamlit.
- Implemented **AutoML**, **SHAP explainability**, **anomaly detection**, and a **forecasting model leaderboard** with 73 passing pytest tests.
- Designed a **tool-calling NL agent** that answers data questions using grounded analytics tools instead of executing arbitrary code.

---

## Strong Bullets (impact + tech)

- Developed an end-to-end **data analysis platform** (FastAPI + Streamlit) that automates profiling, visualization, AutoML, time-series forecasting, and executive reporting on uploaded datasets.
- Built a **forecasting leaderboard** comparing ARIMA, Prophet, and XGBoost with rolling-window backtesting (MAPE/RMSE/MAE) to select the best model and generate confidence-interval forecasts.
- Engineered a **safe NL data analyst agent** with Pydantic-validated tool calling across 8 analytics tools (forecast, SHAP, anomalies, segments), eliminating arbitrary code execution while keeping answers grounded in computed results.

---

## Apple AIML-Targeted Bullets

- Shipped a **responsible ML interface** where an LLM plans and explains but never computes — all statistics flow through validated tool calls to scikit-learn, XGBoost, Prophet, and SHAP pipelines.
- Implemented **model comparison and selection** for tabular and time-series tasks with leaderboard ranking, held-out metrics, and SHAP-based global/local explanations for the winning model.
- Designed an **API-first ML backend** with typed Pydantic contracts, modular service engines, and 73 automated tests covering forecasting, explainability, anomaly detection, and agent routing.

---

## Data Analyst-Targeted Bullets

- Built **Prisma AI** to turn raw CSV/Excel uploads into profiles, correlation insights, segment comparisons, anomaly flags, and forecast charts without manual notebook work.
- Automated **“which segment performs best?”** and **“forecast next month”** workflows via a natural-language agent backed by real aggregations, forecast engines, and citation-backed answers.
- Delivered **executive-ready outputs**: Plotly dashboards, markdown reports, forecasting leaderboards, and plain-English anomaly and SHAP summaries from a single upload.

---

## Software Engineer-Targeted Bullets

- Architected a **FastAPI backend** with 12+ REST endpoints, Pydantic schemas, in-memory session management, and a Streamlit frontend sharing the same service layer.
- Wrote a **73-test pytest suite** covering API integration, ML engines, agent tool selection, and error paths (invalid columns, empty data, missing sessions).
- Applied **clean separation of concerns**: thin routers, reusable analytics services, strict request/response models, and optional Ollama integration without blocking core functionality.

---

## Suggested One-Liner for Projects Section

**Prisma AI** — Python data copilot (FastAPI, Streamlit, scikit-learn, SHAP, XGBoost) with AutoML, forecasting leaderboard, anomaly detection, and a tool-calling NL analyst agent; 73 tests.
