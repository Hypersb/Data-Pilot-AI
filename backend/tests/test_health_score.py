import io

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.health_score_service import compute_health_score

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


@pytest.fixture
def session_id():
    resp = client.post(
        "/api/upload",
        files={"file": ("test.csv", SAMPLE_CSV, "text/csv")},
    )
    assert resp.status_code == 200
    return resp.json()["session_id"]


def test_health_score_service():
    df = pd.read_csv(io.BytesIO(SAMPLE_CSV))
    result = compute_health_score(df)
    assert 0 <= result["overall_score"] <= 100
    assert "completeness" in result["sub_scores"]
    assert result["rows"] == 8


def test_health_endpoint(session_id):
    resp = client.get(f"/api/sessions/{session_id}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_score" in data
    assert len(data["sub_scores"]) == 7
