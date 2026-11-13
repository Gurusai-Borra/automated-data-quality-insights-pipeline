from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END
from .nodes import (
    ingest_node, clean_node, validate_node, route_after_validation,
    retry_node, flag_node, analyze_node, report_node,
)

class PipelineState(TypedDict, total=False):
    input_path: str
    raw_df: Any
    cleaned_df: Any
    validation_errors: list[str]
    validation_passed: bool
    retry_count: int
    duplicate_rows_removed: int
    flagged: bool
    outliers: dict
    metrics: dict
    report_path: str
    step_status: str

def build_pipeline():
    graph = StateGraph(PipelineState)
    graph.add_node("ingest", ingest_node)
    graph.add_node("clean", clean_node)
    graph.add_node("validate", validate_node)
    graph.add_node("retry", retry_node)
    graph.add_node("flag", flag_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("report", report_node)

    graph.add_edge(START, "ingest")
    graph.add_edge("ingest", "clean")
    graph.add_edge("clean", "validate")
    graph.add_conditional_edges("validate", route_after_validation, {
        "retry": "retry", "flag": "flag", "analyze": "analyze"
    })
    graph.add_edge("retry", "clean")
    graph.add_edge("flag", "analyze")
    graph.add_edge("analyze", "report")
    graph.add_edge("report", END)
    return graph.compile()
