import io

import pandas as pd

from app.services.dashboard_service import generate_dashboard


def test_dashboard_config():
    df = pd.read_csv(io.BytesIO(b"date,region,revenue\n2024-01-01,North,100\n2024-02-01,South,200\n"))
    result = generate_dashboard(df)
    assert "kpis" in result
    assert "panels" in result
    assert len(result["kpis"]) >= 1
