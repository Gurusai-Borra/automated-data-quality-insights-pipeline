import pandas as pd
from src.dq_pipeline.validation import validate_dataframe

def test_valid_dataframe_has_no_errors():
    df = pd.DataFrame({
        "customer_id": [1, 2],
        "age": [25, 40],
        "email": ["a@example.com", "b@example.com"],
        "monthly_spend": [10.0, 20.0],
    })
    assert validate_dataframe(df) == []

def test_invalid_dataframe_reports_business_rule_errors():
    df = pd.DataFrame({
        "customer_id": [1, 1],
        "age": [150, None],
        "email": ["not-an-email", "b@example.com"],
        "monthly_spend": [-1, 20],
    })
    errors = validate_dataframe(df)
    assert any("unique" in error for error in errors)
    assert any("between 0 and 120" in error for error in errors)
    assert any("invalid addresses" in error for error in errors)
    assert any("negative" in error for error in errors)
