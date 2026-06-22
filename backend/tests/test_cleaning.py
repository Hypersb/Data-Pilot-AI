import io

import pandas as pd

from app.services.cleaning_agent_service import apply_cleaning, parse_instruction

SAMPLE_CSV = b"""customer,revenue
Alice,100
Alice,100
Bob,
Charlie,200
"""


def test_parse_drop_duplicates():
    ops = parse_instruction("Remove duplicate customers", ["customer", "revenue"])
    assert ops[0][0] == "drop_duplicates"


def test_apply_fillna_median():
    df = pd.read_csv(io.BytesIO(SAMPLE_CSV))
    cleaned, audit = apply_cleaning(df, "Fill missing revenue with median")
    assert len(audit) >= 1
    assert cleaned["revenue"].isna().sum() == 0


def test_apply_drop_duplicates():
    df = pd.read_csv(io.BytesIO(SAMPLE_CSV))
    cleaned, audit = apply_cleaning(df, "Remove duplicate customers")
    assert len(cleaned) < len(df)
