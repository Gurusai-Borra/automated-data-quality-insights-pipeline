import pandas as pd
from .config import REQUIRED_COLUMNS

def validate_dataframe(df: pd.DataFrame) -> list[str]:
    """Return human-readable validation errors; an empty list means valid."""
    errors = []
    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        return [f"Missing required columns: {', '.join(missing_columns)}"]

    if df["customer_id"].isna().any() or (df["customer_id"].astype("string").str.strip() == "").any():
        errors.append("customer_id contains missing or blank values")
    if df["customer_id"].duplicated().any():
        errors.append("customer_id must be unique")

    age = pd.to_numeric(df["age"], errors="coerce")
    if age.isna().any():
        errors.append("age contains missing or non-numeric values")
    if ((age < 0) | (age > 120)).any():
        errors.append("age must be between 0 and 120")

    email = df["email"].astype("string")
    if email.isna().any() or (~email.str.contains(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", na=False)).any():
        errors.append("email contains missing or invalid addresses")

    spend = pd.to_numeric(df["monthly_spend"], errors="coerce")
    if spend.isna().any():
        errors.append("monthly_spend contains missing or non-numeric values")
    if (spend < 0).any():
        errors.append("monthly_spend cannot be negative")

    return errors
