import io

import pandas as pd

from app.services.sql_generation_service import generate_sql


def test_sql_top_n():
    df = pd.read_csv(io.BytesIO(b"customer,revenue\nA,100\nB,200\n"))
    result = generate_sql(df, "Top 10 customers by revenue", "sales")
    assert "SELECT" in result["sql"].upper()
    assert "LIMIT" in result["sql"].upper()
    assert result["explanation"]


def test_sql_no_execution():
    df = pd.read_csv(io.BytesIO(b"customer,revenue\nA,100\n"))
    result = generate_sql(df, "Average revenue", "sales")
    assert "sql" in result
    assert "AVG" in result["sql"].upper() or "SELECT" in result["sql"].upper()
