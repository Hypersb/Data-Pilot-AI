import io

import pandas as pd
import pytest

from app.services.storytelling_service import generate_story

SAMPLE_CSV = b"""date,region,revenue
2024-01-01,North,100
2024-02-01,North,110
2024-03-01,South,90
2024-04-01,South,95
"""


@pytest.mark.asyncio
async def test_storytelling_template():
    df = pd.read_csv(io.BytesIO(SAMPLE_CSV))
    result = await generate_story(df)
    assert result["what_happened"]
    assert result["why_it_happened"]
    assert result["what_to_do_next"]
    assert result["llm_enhanced"] is False
