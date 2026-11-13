import pandas as pd
from src.dq_pipeline.cleaning import clean_dataframe

def test_cleaning_normalizes_columns_trims_text_and_removes_exact_duplicates():
    df = pd.DataFrame({
        "Customer ID": [1, 1],
        " Email ": [" a@example.com ", " a@example.com "],
        "Age": [25, 25],
    })
    result = clean_dataframe(df)
    assert list(result.columns) == ["customer_id", "email", "age"]
    assert len(result) == 1
    assert result.iloc[0]["email"] == "a@example.com"
