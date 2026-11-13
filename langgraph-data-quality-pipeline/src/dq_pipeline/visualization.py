import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def create_quality_charts(df: pd.DataFrame, outlier_results: dict, output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    created = []

    missing = df.isna().sum()
    fig, ax = plt.subplots(figsize=(8, 4))
    missing.plot(kind="bar", ax=ax)
    ax.set_title("Missing Values by Column")
    ax.set_ylabel("Missing count")
    fig.tight_layout()
    path = output_dir / "missing_values.png"
    fig.savefig(path, dpi=140)
    plt.close(fig)
    created.append(str(path))

    counts = {name: info["count"] for name, info in outlier_results.items()}
    fig, ax = plt.subplots(figsize=(8, 4))
    if counts:
        pd.Series(counts).plot(kind="bar", ax=ax)
    ax.set_title("IQR Outliers by Numeric Column")
    ax.set_ylabel("Outlier count")
    fig.tight_layout()
    path = output_dir / "numeric_outliers.png"
    fig.savefig(path, dpi=140)
    plt.close(fig)
    created.append(str(path))
    return created
