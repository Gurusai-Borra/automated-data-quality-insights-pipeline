import pandas as pd

def load_csv(path: str) -> pd.DataFrame:
    """Load a CSV file and return a DataFrame."""
    try:
        return pd.read_csv(path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Input CSV was not found: {path}") from exc
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"Input CSV is empty: {path}") from exc
