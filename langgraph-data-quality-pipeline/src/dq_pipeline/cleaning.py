import pandas as pd
from .config import NUMERIC_COLUMNS

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply repeatable, conservative cleaning operations."""
    cleaned = df.copy()
    cleaned.columns = [str(col).strip().lower().replace(" ", "_") for col in cleaned.columns]
    cleaned = cleaned.drop_duplicates().copy()

    for col in cleaned.select_dtypes(include=["object"]).columns:
        cleaned[col] = cleaned[col].astype("string").str.strip()

    for col in NUMERIC_COLUMNS:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    return cleaned
