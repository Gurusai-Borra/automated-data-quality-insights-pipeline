import pandas as pd

def detect_iqr_outliers(df: pd.DataFrame, columns: list[str] | None = None) -> dict:
    """Detect IQR outliers and return row counts plus index labels per column."""
    columns = columns or df.select_dtypes(include="number").columns.tolist()
    results = {}
    for col in columns:
        if col not in df.columns:
            continue
        values = pd.to_numeric(df[col], errors="coerce").dropna()
        if values.empty:
            results[col] = {"count": 0, "indices": []}
            continue
        q1, q3 = values.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask = pd.to_numeric(df[col], errors="coerce").lt(lower) | pd.to_numeric(df[col], errors="coerce").gt(upper)
        results[col] = {"count": int(mask.sum()), "indices": df.index[mask].tolist()}
    return results
