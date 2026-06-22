# Prisma AI V3 — 3-Minute Demo Script

Use the sample dataset for live demos: **Upload → Try sample dataset (recommended for demos)**.

## Setup (before the meeting)

1. Run `.\scripts\start-dev.ps1` from the project root
2. Open http://localhost:3000
3. Confirm backend: http://127.0.0.1:8080/health shows `"version":"3.0.0"`

## Minute 1 — Upload and automatic analysis

1. Click **Upload file** or **Try sample dataset**
2. Land on **Overview** (Analysis Hub)
3. Point out:
   - Row/column counts and quality score
   - Top 3 insights with severity badges
   - Auto-generated charts
   - Forecast preview (or graceful “not applicable” message)

**Say:** “Prisma runs EDA, insight detection, and forecast screening automatically — no manual setup.”

## Minute 2 — Insights and forecast

1. Click step **2 Insights** in the sidebar
2. Scroll through ranked insights and EDA charts
3. Click step **3 Forecast**
4. Show model leaderboard and forecast chart (time-series data) or explain fallback

**Say:** “Every number is computed in Python — Pandas, scikit-learn, Prophet, XGBoost — not hallucinated.”

## Minute 3 — Chat and PDF report

1. Click **Ask a question** or step **4 Chat**
2. Chat auto-bootstraps with a dataset summary (or ask: “Which region performs best?”)
3. Point out tool name, confidence, and citations
4. Click step **5 Report** → **Download PDF**

**Say:** “You get a business report plus a conversational analyst grounded in the same engine.”

## Optional — Advanced (if asked)

Open **Advanced** in the sidebar for V2 depth:

- Root cause analysis with contribution percentages
- Multi-agent team analysis
- NL data cleaning with audit trail
- SQL generation (educational, non-executing)

## Closing line

“Prisma AI is my graduation-ready AI Business Analyst — upload data, get insights, forecasts, and a PDF report, then talk to your data in plain English.”
