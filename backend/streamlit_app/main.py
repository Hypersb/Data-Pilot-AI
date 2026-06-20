"""Prisma AI — Streamlit dashboard (Python UI)."""

import asyncio
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "static" / "logo.png"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings
from app.services.anomaly_engine import detect_anomalies
from app.services.automl_engine import run_automl
from app.services.forecast_engine import run_forecast_leaderboard
from app.services.xai_engine import run_xai_explanation
from app.services.ingest import parse_upload
from app.services.insight_engine import generate_insights
from app.services.agent_engine import run_agent_chat
from app.services.profiler import profile_dataframe
from app.services.report_engine import generate_report
from app.services.session_store import session_store
from app.services.viz_engine import generate_charts

st.set_page_config(
    page_title="Prisma AI",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

SEVERITY_COLORS = {
    "high": "🔴",
    "medium": "🟠",
    "low": "🔵",
    "info": "⚪",
}


def init_state() -> None:
    defaults = {
        "session_id": None,
        "filename": None,
        "chat_history": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def run_async(coro):
    return asyncio.run(coro)


def load_dataset(uploaded_file) -> None:
    content = uploaded_file.getvalue()
    if len(content) > settings.max_upload_bytes:
        st.error(f"File too large. Maximum size is {settings.max_upload_mb} MB.")
        return
    try:
        df = parse_upload(content, uploaded_file.name)
    except ValueError as exc:
        st.error(str(exc))
        return

    session_id = session_store.create(df, uploaded_file.name)
    st.session_state.session_id = session_id
    st.session_state.filename = uploaded_file.name
    st.session_state.chat_history = []
    st.success(f"Loaded **{uploaded_file.name}** — {len(df):,} rows, {len(df.columns)} columns")
    st.rerun()


def get_dataframe() -> pd.DataFrame | None:
    sid = st.session_state.session_id
    if not sid:
        return None
    return session_store.get(sid)


def render_upload() -> None:
    st.markdown("### Upload your dataset")
    st.caption("CSV or Excel (.xlsx, .xls) — up to 25 MB")
    uploaded = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed",
    )
    if uploaded is not None:
        load_dataset(uploaded)

    sample_path = ROOT.parent / "sample-data" / "sales.csv"
    if sample_path.exists():
        st.markdown("---")
        if st.button("Try sample sales dataset"):
            content = sample_path.read_bytes()
            df = parse_upload(content, "sales.csv")
            session_id = session_store.create(df, "sales.csv")
            st.session_state.session_id = session_id
            st.session_state.filename = "sales.csv"
            st.session_state.chat_history = []
            st.rerun()


def render_overview(df: pd.DataFrame) -> None:
    profile = profile_dataframe(df)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Rows", f"{profile['rows']:,}")
    c2.metric("Columns", profile["columns"])
    c3.metric("Quality Score", f"{profile['quality_score']}/100")
    c4.metric("Completeness", f"{profile['completeness_pct']}%")
    c5.metric("Duplicates", profile["duplicate_rows"])
    c6.metric("Missing Cells", profile["missing_cells"])

    if profile["quality_flags"]:
        with st.expander("Data quality flags", expanded=True):
            for flag in profile["quality_flags"]:
                st.warning(flag)

    st.markdown("#### Column details")
    st.dataframe(
        pd.DataFrame(profile["columns_info"])[
            ["name", "dtype", "null_count", "null_pct", "unique_count"]
        ],
        use_container_width=True,
        hide_index=True,
    )


def render_insights(df: pd.DataFrame) -> None:
    insights = generate_insights(df)
    if not insights:
        st.info("No insights generated for this dataset.")
        return
    for insight in insights:
        icon = SEVERITY_COLORS.get(insight["severity"], "⚪")
        with st.container(border=True):
            st.markdown(f"**{icon} {insight['title']}**")
            st.caption(f"{insight['type'].replace('_', ' ').title()} · {insight['severity']}")
            st.write(insight["description"])
            if insight["related_columns"]:
                st.markdown(
                    "Columns: "
                    + ", ".join(f"`{c}`" for c in insight["related_columns"])
                )


def render_charts(df: pd.DataFrame) -> None:
    charts = generate_charts(df)
    if not charts:
        st.info("No charts available for this dataset.")
        return
    cols = st.columns(2)
    for i, chart in enumerate(charts):
        with cols[i % 2]:
            fig = go.Figure(chart["figure"])
            fig.update_layout(margin=dict(l=40, r=20, t=40, b=40))
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{chart['id']}")


def render_forecast(df: pd.DataFrame) -> None:
    profile = profile_dataframe(df)
    numeric_cols = [
        c["name"] for c in profile["columns_info"] if c["dtype"] == "numeric"
    ]
    date_cols = [
        c["name"] for c in profile["columns_info"] if c["dtype"] == "datetime"
    ]

    if not numeric_cols or not date_cols:
        st.warning("Forecasting requires a datetime column and a numeric target column.")
        return

    st.caption("Datetime and numeric target detected — forecasting is available.")

    c1, c2, c3 = st.columns(3)
    with c1:
        date_column = st.selectbox("Date column", date_cols)
    with c2:
        target_column = st.selectbox("Target column", numeric_cols)
    with c3:
        forecast_horizon = st.slider("Forecast horizon", 1, 24, 6)

    if st.button("Run forecast leaderboard", type="primary"):
        try:
            result = run_forecast_leaderboard(
                df,
                target_column=target_column,
                date_column=date_column,
                forecast_horizon=forecast_horizon,
            )
            st.session_state.forecast_result = result
        except ValueError as exc:
            st.error(str(exc))

    result = st.session_state.get("forecast_result")
    if not result:
        return

    best = result["best_model"]
    st.success(result["explanation"])
    st.caption(
        f"Best model: **{best['model_name']}** · "
        f"MAPE **{best['metrics']['mape']:.2f}%** · "
        f"RMSE **{best['metrics']['rmse']:.2f}** · "
        f"MAE **{best['metrics']['mae']:.2f}**"
    )

    chart_json = result["chart_data"].get("forecast_chart")
    if chart_json:
        st.plotly_chart(go.Figure(chart_json), use_container_width=True)
    else:
        fig = go.Figure()
        hist = result["historical"]
        fc = result["forecast"]
        fig.add_trace(
            go.Scatter(
                x=[h["date"] for h in hist],
                y=[h["value"] for h in hist],
                mode="lines+markers",
                name="Historical",
                line=dict(color="#6366f1"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[f["date"] for f in fc],
                y=[f["value"] for f in fc],
                mode="lines+markers",
                name="Forecast",
                line=dict(color="#a855f7", dash="dash"),
            )
        )
        if fc and "lower" in fc[0] and "upper" in fc[0]:
            fig.add_trace(
                go.Scatter(
                    x=[f["date"] for f in fc] + [f["date"] for f in fc][::-1],
                    y=[f["upper"] for f in fc] + [f["lower"] for f in fc][::-1],
                    fill="toself",
                    fillcolor="rgba(168, 85, 247, 0.15)",
                    line=dict(color="rgba(168, 85, 247, 0)"),
                    name="Confidence interval",
                )
            )
        fig.update_layout(
            title=f"Forecast: {result['target_column']}",
            xaxis_title="Date",
            yaxis_title=result["target_column"],
            margin=dict(l=40, r=20, t=40, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    leaderboard_rows = []
    for entry in result["leaderboard"]:
        leaderboard_rows.append(
            {
                "Rank": entry["rank"],
                "Model": entry["model_name"] + (" ★" if entry.get("is_best") else ""),
                "MAPE (%)": entry["metrics"]["mape"],
                "RMSE": entry["metrics"]["rmse"],
                "MAE": entry["metrics"]["mae"],
            }
        )
    st.subheader("Forecasting leaderboard")
    st.dataframe(
        pd.DataFrame(leaderboard_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Forecast values")
    st.dataframe(
        pd.DataFrame(result["forecast"]),
        use_container_width=True,
        hide_index=True,
    )


def render_automl(df: pd.DataFrame) -> None:
    profile = profile_dataframe(df)
    numeric_cols = [
        c["name"] for c in profile["columns_info"] if c["dtype"] == "numeric"
    ]
    date_cols = [
        c["name"] for c in profile["columns_info"] if c["dtype"] == "datetime"
    ]
    categorical_cols = [
        c["name"] for c in profile["columns_info"] if c["dtype"] == "categorical"
    ]
    target_options = list(dict.fromkeys(numeric_cols + categorical_cols))

    if not target_options:
        st.warning("No suitable target columns found for AutoML.")
        return

    c1, c2, _ = st.columns(3)
    with c1:
        target_column = st.selectbox(
            "Target column (auto-detected if blank)",
            ["Auto-detect"] + target_options,
            key="automl_target",
        )
    with c2:
        date_column = st.selectbox(
            "Date column (for forecasting)",
            ["Auto-detect"] + date_cols if date_cols else ["Auto-detect"],
            key="automl_date",
        )

    if st.button("Run AutoML", type="primary", key="run_automl"):
        with st.spinner("Training and evaluating models..."):
            try:
                result = run_automl(
                    df,
                    target_column=None if target_column == "Auto-detect" else target_column,
                    date_column=(
                        None
                        if date_column == "Auto-detect" or not date_cols
                        else date_column
                    ),
                )
                st.session_state.automl_result = result
            except ValueError as exc:
                st.error(str(exc))

    result = st.session_state.get("automl_result")
    if not result:
        st.info("Click **Run AutoML** to detect the task type and train models.")
        return

    st.success(f"Detected task: **{result['task_type'].replace('_', ' ').title()}**")
    st.caption(result["detection_reason"])

    m1, m2, m3 = st.columns(3)
    m1.metric("Target", result["target_column"])
    m2.metric("Models trained", result["models_trained"])
    m3.metric("Best model", result["best_model"]["model_name"])

    st.markdown("#### Model leaderboard")
    leaderboard_rows = []
    for entry in result["leaderboard"]:
        row = {
            "Rank": entry.get("rank"),
            "Model": entry["model_name"],
            "Best": "Yes" if entry.get("is_best") else "",
            **entry["metrics"],
        }
        leaderboard_rows.append(row)

    st.dataframe(
        pd.DataFrame(leaderboard_rows),
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("Structured JSON output"):
        st.json(result)


def render_anomalies(df: pd.DataFrame) -> None:
    if st.button("Run anomaly detection", type="primary", key="run_anomalies"):
        with st.spinner("Detecting anomalies..."):
            result = detect_anomalies(df)
            st.session_state.anomaly_result = result

    result = st.session_state.get("anomaly_result")
    if not result:
        st.info("Click **Run anomaly detection** to scan for unusual rows and values.")
        return

    if not result.get("available"):
        st.warning(result["plain_english_explanation"])
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Total anomalies", result["total_anomalies"])
    c2.metric("Severity score", f"{result['severity_score']}/100")
    c3.metric("Methods used", len(result["anomaly_methods_used"]))

    st.success(result["plain_english_explanation"])
    st.caption(result["anomaly_summary"])

    if result["anomaly_methods_used"]:
        st.markdown(
            "Methods: "
            + ", ".join(f"`{method}`" for method in result["anomaly_methods_used"])
        )

    if result["chart_data"].get("anomaly_chart"):
        st.plotly_chart(
            go.Figure(result["chart_data"]["anomaly_chart"]),
            use_container_width=True,
            key="anomaly_chart",
        )

    if result["top_anomalous_columns"]:
        st.markdown("#### Top anomalous columns")
        st.dataframe(
            pd.DataFrame(result["top_anomalous_columns"]),
            use_container_width=True,
            hide_index=True,
        )

    if result["anomaly_rows"]:
        st.markdown("#### Anomalous rows")
        table_rows = [
            {
                "Row": row["row_index"],
                "Severity": row["severity"],
                "Methods": ", ".join(row["methods"]),
                "Columns": ", ".join(row["columns"]),
                "Explanation": row["explanation"],
            }
            for row in result["anomaly_rows"]
        ]
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No anomalous rows detected.")

    with st.expander("Structured JSON output"):
        st.json(result)


def render_explain(df: pd.DataFrame) -> None:
    profile = profile_dataframe(df)
    numeric_cols = [
        c["name"] for c in profile["columns_info"] if c["dtype"] == "numeric"
    ]
    categorical_cols = [
        c["name"] for c in profile["columns_info"] if c["dtype"] == "categorical"
    ]
    target_options = list(dict.fromkeys(numeric_cols + categorical_cols))

    if not target_options:
        st.warning("No suitable target columns found for SHAP explanations.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        target_column = st.selectbox(
            "Target column",
            ["Auto-detect"] + target_options,
            key="explain_target",
        )
    with c2:
        row_index = st.number_input(
            "Local explanation row index (optional)",
            min_value=0,
            value=0,
            step=1,
            key="explain_row",
        )
    with c3:
        use_row = st.checkbox("Explain specific row only", value=False, key="explain_use_row")

    if st.button("Generate SHAP explanations", type="primary", key="run_explain"):
        with st.spinner("Training best AutoML model and computing SHAP values..."):
            try:
                result = run_xai_explanation(
                    df,
                    target_column=None if target_column == "Auto-detect" else target_column,
                    row_index=row_index if use_row else 0,
                )
                st.session_state.xai_result = result
            except ValueError as exc:
                st.error(str(exc))

    result = st.session_state.get("xai_result")
    if not result:
        st.info(
            "Run SHAP analysis on the best AutoML model to see global and local feature importance. "
            "Supported for regression and classification tasks."
        )
        return

    if not result.get("available"):
        st.warning(result["global_explanation"])
        return

    st.success(result["global_explanation"])
    st.caption(f"Best model: **{result['model_name']}** · Target: **{result['target_column']}**")

    if result["chart_data"].get("importance_bar"):
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                go.Figure(result["chart_data"]["importance_bar"]),
                use_container_width=True,
                key="xai_importance",
            )
        with col2:
            if result["chart_data"].get("summary_plot"):
                st.plotly_chart(
                    go.Figure(result["chart_data"]["summary_plot"]),
                    use_container_width=True,
                    key="xai_summary",
                )

    st.markdown("#### Top 10 global features")
    st.dataframe(
        pd.DataFrame(result["top_features"])[
            ["rank", "display_name", "importance", "direction", "mean_shap_value"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Local prediction explanations")
    for item in result["local_explanations"]:
        with st.container(border=True):
            st.markdown(f"**Row {item['row_index']}** · Prediction: `{item['prediction']}`")
            st.write(item["narrative"])
            st.dataframe(
                pd.DataFrame(item["top_contributors"]),
                use_container_width=True,
                hide_index=True,
            )

    with st.expander("Structured JSON output"):
        st.json(result)


def render_report(df: pd.DataFrame) -> None:
    filename = st.session_state.filename or "dataset"
    if st.button("Generate executive report", type="primary"):
        with st.spinner("Generating report..."):
            result = run_async(generate_report(df, filename))
            st.session_state.report = result

    report = st.session_state.get("report")
    if not report:
        st.info("Click **Generate executive report** to create your report.")
        return

    if report["llm_enhanced"]:
        st.success("AI-enhanced report (Ollama)")
    else:
        st.info("Template report (Ollama unavailable — using structured template)")

    st.markdown(report["markdown"])
    st.download_button(
        "Download report (.md)",
        data=report["markdown"],
        file_name=f"prisma-ai-report-{filename.rsplit('.', 1)[0]}.md",
        mime="text/markdown",
    )


def render_chat(df: pd.DataFrame) -> None:
    suggestions = [
        "Which region generated the most revenue?",
        "What caused sales to drop?",
        "Forecast next month's revenue.",
        "Show me unusual records.",
        "What variables influence profit most?",
        "Which customer segment performs best?",
    ]
    st.caption("Ask questions about your data in plain English. Answers are grounded in your dataset via tool execution.")
    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        if cols[i % 3].button(suggestion, key=f"suggest_{i}"):
            st.session_state.pending_question = suggestion

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tool_used"):
                st.caption(
                    f"Tool: `{msg['tool_used']}` · Confidence: **{msg.get('confidence', 0):.0%}**"
                )
            if msg.get("citations"):
                with st.expander("Sources"):
                    for cite in msg["citations"][:8]:
                        st.markdown(f"- {cite}")
            chart_data = msg.get("chart_data") or {}
            for key in ("bar_chart", "forecast_chart", "anomaly_chart", "importance_bar"):
                if chart_data.get(key):
                    st.plotly_chart(go.Figure(chart_data[key]), use_container_width=True)
            if msg.get("chart") and not chart_data:
                st.plotly_chart(go.Figure(msg["chart"]), use_container_width=True)
            if msg.get("follow_up_questions"):
                st.markdown("**Follow-up ideas:** " + " · ".join(f"`{q}`" for q in msg["follow_up_questions"][:3]))

    question = st.chat_input("Ask about your data...")
    if st.session_state.get("pending_question"):
        question = st.session_state.pending_question
        st.session_state.pending_question = None

    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.spinner("Analyzing with data tools..."):
            try:
                result = run_async(run_agent_chat(df, question, st.session_state.chat_history))
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": result["answer"],
                        "tool_used": result.get("tool_used"),
                        "confidence": result.get("confidence"),
                        "citations": result.get("citations", []),
                        "chart_data": result.get("chart_data", {}),
                        "follow_up_questions": result.get("follow_up_questions", []),
                    }
                )
            except Exception as exc:
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": f"Error: {exc}",
                    }
                )
        st.rerun()


def main() -> None:
    init_state()

    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=72)
    st.title("Prisma AI")
    st.markdown("**Intelligent Data Analysis Copilot** — automated insights, forecasts, and reports")

    with st.sidebar:
        st.header("Dataset")
        if st.session_state.session_id:
            st.success(st.session_state.filename or "Loaded")
            if st.button("Clear session"):
                session_store.delete(st.session_state.session_id)
                st.session_state.session_id = None
                st.session_state.filename = None
                st.session_state.chat_history = []
                st.session_state.pop("forecast_result", None)
                st.session_state.pop("automl_result", None)
                st.session_state.pop("anomaly_result", None)
                st.session_state.pop("xai_result", None)
                st.session_state.pop("report", None)
                st.rerun()
        else:
            st.info("No dataset loaded")
        st.markdown("---")
        st.markdown("**Stack:** Python · FastAPI · Streamlit · Plotly")
        st.markdown(f"Ollama: `{settings.ollama_base_url}`")

    df = get_dataframe()

    if df is None:
        render_upload()
        return

    tabs = st.tabs(
        [
            "Overview",
            "Insights",
            "Anomalies",
            "Charts",
            "Forecast",
            "AutoML",
            "Explainable AI",
            "Report",
            "AI Data Analyst",
        ]
    )
    with tabs[0]:
        render_overview(df)
    with tabs[1]:
        render_insights(df)
    with tabs[2]:
        render_anomalies(df)
    with tabs[3]:
        render_charts(df)
    with tabs[4]:
        render_forecast(df)
    with tabs[5]:
        render_automl(df)
    with tabs[6]:
        render_explain(df)
    with tabs[7]:
        render_report(df)
    with tabs[8]:
        render_chat(df)


if __name__ == "__main__":
    main()
