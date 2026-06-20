from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_CSV = b"""date,region,product,revenue
2024-01-01,North,A,100
2024-02-01,North,A,110
2024-03-01,North,A,120
2024-04-01,South,B,90
2024-05-01,South,B,95
2024-06-01,South,B,100
2024-07-01,North,A,130
2024-08-01,North,A,140
"""


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_upload_and_profile_flow():
    resp = client.post(
        "/api/upload",
        files={"file": ("test.csv", SAMPLE_CSV, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    session_id = data["session_id"]
    assert data["rows"] == 8

    profile = client.get(f"/api/sessions/{session_id}/profile")
    assert profile.status_code == 200
    assert profile.json()["rows"] == 8

    insights = client.get(f"/api/sessions/{session_id}/insights")
    assert insights.status_code == 200
    assert insights.json()["count"] >= 1

    charts = client.get(f"/api/sessions/{session_id}/charts")
    assert charts.status_code == 200
    assert charts.json()["count"] >= 1

    forecast = client.post(
        f"/api/sessions/{session_id}/forecast",
        json={"periods": 2},
    )
    assert forecast.status_code == 200
    assert len(forecast.json()["forecast"]) == 2

    forecast_get = client.get(
        f"/api/sessions/{session_id}/forecast",
        params={"forecast_horizon": 2},
    )
    assert forecast_get.status_code == 200
    leaderboard = forecast_get.json()
    assert leaderboard["available"] is True
    assert len(leaderboard["leaderboard"]) >= 1
    assert leaderboard["best_model"]["is_best"] is True
    assert len(leaderboard["forecast"]) == 2

    query = client.post(
        f"/api/sessions/{session_id}/query",
        json={"question": "Summarize this dataset"},
    )
    assert query.status_code == 200
    assert query.json()["answer"]

    chat = client.post(
        f"/api/sessions/{session_id}/chat",
        json={"question": "Which region has the highest revenue?"},
    )
    assert chat.status_code == 200
    chat_data = chat.json()
    assert chat_data["tool_used"]
    assert chat_data["answer"]

    report = client.get(f"/api/sessions/{session_id}/report")
    assert report.status_code == 200
    assert "Executive" in report.json()["markdown"] or "Report" in report.json()["markdown"]

    delete = client.delete(f"/api/sessions/{session_id}")
    assert delete.status_code == 200


AUTOML_CSV = b"""feature_a,feature_b,revenue
1.0,2.0,10.5
2.0,3.0,15.2
3.0,4.0,18.1
4.0,5.0,22.0
5.0,6.0,25.5
6.0,7.0,28.3
7.0,8.0,31.0
8.0,9.0,34.2
9.0,10.0,37.5
10.0,11.0,40.0
11.0,12.0,43.1
12.0,13.0,46.0
"""


def test_automl_endpoint():
    resp = client.post(
        "/api/upload",
        files={"file": ("automl.csv", AUTOML_CSV, "text/csv")},
    )
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]

    automl = client.post(
        f"/api/sessions/{session_id}/automl",
        json={"target_column": "revenue"},
    )
    assert automl.status_code == 200
    data = automl.json()
    assert data["task_type"] == "regression"
    assert data["best_model"]["model_name"]
    assert len(data["leaderboard"]) >= 2
    assert any(row["is_best"] for row in data["leaderboard"])


EXPLAIN_CSV = AUTOML_CSV


def test_xai_endpoint():
    resp = client.post(
        "/api/upload",
        files={"file": ("xai.csv", EXPLAIN_CSV, "text/csv")},
    )
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]

    xai = client.get(
        f"/api/sessions/{session_id}/xai",
        params={"target_column": "revenue", "row_index": 0},
    )
    assert xai.status_code == 200
    data = xai.json()
    assert data["available"] is True
    assert data["model_name"]
    assert data["global_explanation"]
    assert len(data["top_features"]) >= 1
    assert data["chart_data"]["importance_bar"]
    assert len(data["local_explanations"]) == 1


def test_xai_invalid_session():
    resp = client.get("/api/sessions/00000000-0000-0000-0000-000000000000/xai")
    assert resp.status_code == 404


ANOMALY_CSV = b"""value,score
10,1
11,1
12,1
13,1
14,1
15,1
16,1
17,1
18,1
200,1
"""


def test_anomalies_endpoint():
    resp = client.post(
        "/api/upload",
        files={"file": ("anomaly.csv", ANOMALY_CSV, "text/csv")},
    )
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]

    anomalies = client.get(f"/api/sessions/{session_id}/anomalies")
    assert anomalies.status_code == 200
    data = anomalies.json()
    assert data["available"] is True
    assert data["total_anomalies"] >= 1
    assert data["anomaly_methods_used"]
    assert data["plain_english_explanation"]
    assert "anomaly_chart" in data["chart_data"]


def test_anomalies_invalid_session():
    resp = client.get("/api/sessions/00000000-0000-0000-0000-000000000000/anomalies")
    assert resp.status_code == 404
