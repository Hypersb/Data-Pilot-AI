import io

import pandas as pd
import pytest

from app.services.report_service import generate_full_report

SAMPLE_CSV = b"""date,region,revenue
2024-01-01,North,100
2024-02-01,North,110
"""


@pytest.mark.asyncio
async def test_report_markdown():
    df = pd.read_csv(io.BytesIO(SAMPLE_CSV))
    result = await generate_full_report(df, "test.csv", fmt="markdown")
    assert result["executive_summary"]
    assert result["key_findings"] is not None
    assert result.get("scqa")
    assert result.get("prioritized_recommendations")
    assert result.get("forecast_outlook")


@pytest.mark.asyncio
async def test_report_pdf_bytes():
    df = pd.read_csv(io.BytesIO(SAMPLE_CSV))
    result = await generate_full_report(df, "test.csv", fmt="pdf")
    assert len(result["file_bytes"]) > 100
    assert result["file_bytes"][:4] == b"%PDF"


@pytest.mark.asyncio
async def test_report_pptx_bytes():
    df = pd.read_csv(io.BytesIO(SAMPLE_CSV))
    result = await generate_full_report(df, "test.csv", fmt="pptx")
    assert len(result["file_bytes"]) > 100
    assert result["file_bytes"][:2] == b"PK"
