import io

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_CSV = b"""date,region,revenue
2024-01-01,North,100
2024-02-01,North,110
2024-03-01,South,90
2024-04-01,South,95
"""


@pytest.fixture
def session_id():
    resp = client.post(
        "/api/upload",
        files={"file": ("test.csv", SAMPLE_CSV, "text/csv")},
    )
    return resp.json()["session_id"]


def test_analysis_bundle(session_id):
    resp = client.get(f"/api/sessions/{session_id}/analysis")
    assert resp.status_code == 200
    data = resp.json()
    assert data["profile"]["rows"] == 4
    assert data["insight_count"] >= 0
    assert "dashboard" in data
    assert "forecast_message" in data
