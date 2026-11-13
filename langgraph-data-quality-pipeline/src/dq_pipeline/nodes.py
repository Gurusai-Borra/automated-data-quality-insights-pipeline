import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

from .config import OUTPUT_DIR, LOG_DIR, MAX_VALIDATION_RETRIES
from .ingestion import load_csv
from .cleaning import clean_dataframe
from .validation import validate_dataframe
from .anomalies import detect_iqr_outliers
from .visualization import create_quality_charts
from .summarization import summarize_findings

def _logger():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("dq_pipeline")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    return logger

def ingest_node(state: dict) -> dict:
    logger = _logger()
    df = load_csv(state["input_path"])
    logger.info("Ingestion completed: %s rows, %s columns", len(df), len(df.columns))
    return {"raw_df": df, "step_status": "ingested"}

def clean_node(state: dict) -> dict:
    logger = _logger()
    source = state.get("raw_df") if state.get("retry_count", 0) == 0 else state.get("cleaned_df")
    source = source if source is not None else state["raw_df"]
    before = len(source)
    cleaned = clean_dataframe(source)
    logger.info("Cleaning completed: %s exact duplicates removed", before - len(cleaned))
    return {"cleaned_df": cleaned, "duplicate_rows_removed": state.get("duplicate_rows_removed", 0) + before - len(cleaned),
            "step_status": "cleaned"}

def validate_node(state: dict) -> dict:
    errors = validate_dataframe(state["cleaned_df"])
    logger = _logger()
    logger.info("Validation completed: %s error(s)", len(errors))
    return {"validation_errors": errors, "validation_passed": len(errors) == 0, "step_status": "validated"}

def route_after_validation(state: dict) -> str:
    if state.get("validation_passed"):
        return "analyze"
    if state.get("retry_count", 0) < MAX_VALIDATION_RETRIES:
        return "retry"
    return "flag"

def retry_node(state: dict) -> dict:
    count = state.get("retry_count", 0) + 1
    _logger().warning("Validation failed; starting cleaning retry %s", count)
    return {"retry_count": count, "step_status": "retrying"}

def flag_node(state: dict) -> dict:
    _logger().warning("Validation remains unsuccessful; records/issues are flagged in report")
    return {"flagged": True, "step_status": "flagged"}

def analyze_node(state: dict) -> dict:
    df = state["cleaned_df"]
    outliers = detect_iqr_outliers(df)
    metrics = {
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows_removed": int(state.get("duplicate_rows_removed", 0)),
        "validation_passed": bool(state.get("validation_passed")),
        "validation_error_count": len(state.get("validation_errors", [])),
        "retry_count": int(state.get("retry_count", 0)),
        "flagged": bool(state.get("flagged", False)),
        "outlier_counts": {k: v["count"] for k, v in outliers.items()},
    }
    _logger().info("Anomaly analysis completed")
    return {"outliers": outliers, "metrics": metrics, "step_status": "analyzed"}

def report_node(state: dict) -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = state["cleaned_df"]
    df.to_csv(OUTPUT_DIR / "cleaned_data.csv", index=False)
    charts = create_quality_charts(df, state.get("outliers", {}), OUTPUT_DIR)
    summary = summarize_findings(state["metrics"], state.get("validation_errors", []), state.get("outliers", {}))
    report = [
        "# Data Quality Report", "",
        f"**Run timestamp (UTC):** {state['metrics']['run_timestamp_utc']}",
        f"**Overall status:** {'FLAGGED' if state.get('flagged') else 'PASSED'}",
        "", "## Summary", "", summary, "", "## Validation findings", "",
    ]
    report += [f"- {err}" for err in state.get("validation_errors", [])] or ["- No validation errors."]
    report += ["", "## Anomaly counts", ""]
    report += [f"- {col}: {info['count']} potential outlier(s)" for col, info in state.get("outliers", {}).items()]
    report += ["", "## Generated charts", ""] + [f"- `{Path(p).name}`" for p in charts]
    (OUTPUT_DIR / "quality_report.md").write_text("\n".join(report), encoding="utf-8")
    (OUTPUT_DIR / "quality_metrics.json").write_text(json.dumps(state["metrics"], indent=2), encoding="utf-8")
    _logger().info("Report generation completed")
    return {"report_path": str(OUTPUT_DIR / "quality_report.md"), "step_status": "completed"}
