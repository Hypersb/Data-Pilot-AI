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


def _upload():
    resp = client.post(
        "/api/upload",
        files={"file": ("test.csv", SAMPLE_CSV, "text/csv")},
    )
    return resp.json()["session_id"]


def test_v2_endpoints_flow():
    sid = _upload()

    health = client.get(f"/api/sessions/{sid}/health")
    assert health.status_code == 200

    story = client.get(f"/api/sessions/{sid}/story")
    assert story.status_code == 200
    assert story.json()["what_happened"]

    dashboard = client.get(f"/api/sessions/{sid}/dashboard")
    assert dashboard.status_code == 200
    assert dashboard.json()["kpis"]

    root = client.post(
        f"/api/sessions/{sid}/root-cause",
        json={"metric_column": "revenue", "period_column": "date"},
    )
    assert root.status_code == 200
    assert root.json()["contributors"]

    period = client.post(
        f"/api/sessions/{sid}/compare/period",
        json={"metric_column": "revenue", "date_column": "date", "period": "mom"},
    )
    assert period.status_code == 200

    sql = client.post(
        f"/api/sessions/{sid}/sql",
        json={"question": "Top 10 customers by revenue"},
    )
    assert sql.status_code == 200
    assert "SELECT" in sql.json()["sql"].upper()

    clean = client.post(
        f"/api/sessions/{sid}/clean",
        json={"instruction": "Remove duplicate customers", "replace_in_place": False},
    )
    assert clean.status_code == 200
    assert clean.json()["audit_trail"]

    report = client.get(f"/api/sessions/{sid}/report/v2?format=markdown")
    assert report.status_code == 200
    assert report.json()["executive_summary"]

    team = client.post(f"/api/sessions/{sid}/team-analysis")
    assert team.status_code == 200
    assert team.json()["combined_recommendations"]

    experiments = client.get(f"/api/sessions/{sid}/experiments")
    assert experiments.status_code == 200
