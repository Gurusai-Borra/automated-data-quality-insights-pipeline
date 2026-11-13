import os

def summarize_findings(metrics: dict, validation_errors: list[str], outliers: dict) -> str:
    """Use an LLM when configured; otherwise return a deterministic summary."""
    prompt_data = {
        "metrics": metrics,
        "validation_errors": validation_errors,
        "outlier_counts": {k: v["count"] for k, v in outliers.items()},
    }
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage, SystemMessage
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            llm = ChatOpenAI(model=model, temperature=0)
            response = llm.invoke([
                SystemMessage(content=(
                    "You are a data quality analyst. Summarize aggregate data quality findings in plain language. "
                    "Give 2-4 practical recommendations. Do not invent facts or expose row-level data."
                )),
                HumanMessage(content=f"Analyze these aggregate findings: {prompt_data}"),
            ])
            return str(response.content)
        except Exception as exc:
            return _fallback_summary(metrics, validation_errors, outliers) + f"\n\nLLM summary unavailable: {type(exc).__name__}."

    return _fallback_summary(metrics, validation_errors, outliers)

def _fallback_summary(metrics: dict, errors: list[str], outliers: dict) -> str:
    total_outliers = sum(item["count"] for item in outliers.values())
    status = "passed" if not errors else "flagged"
    lines = [
        f"The data quality validation {status}.",
        f"The dataset contains {metrics.get('row_count', 0)} rows and {metrics.get('column_count', 0)} columns.",
        f"There are {metrics.get('missing_cells', 0)} missing cells and {metrics.get('duplicate_rows_removed', 0)} exact duplicate rows were removed during cleaning.",
        f"The IQR scan identified {total_outliers} potential numeric outlier(s).",
    ]
    if errors:
        lines.append("Issues to review: " + "; ".join(errors))
    lines.append("Recommendations: investigate flagged records, confirm business rules, and review outliers before using the data for decisions.")
    return "\n".join(lines)
