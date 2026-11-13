import argparse
from dotenv import load_dotenv
from src.dq_pipeline.config import DEFAULT_INPUT
from src.dq_pipeline.graph import build_pipeline

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run the LangGraph data quality pipeline")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to input CSV")
    args = parser.parse_args()

    app = build_pipeline()
    result = app.invoke({"input_path": args.input, "retry_count": 0, "duplicate_rows_removed": 0})
    print(f"Pipeline status: {result.get('step_status')}")
    print(f"Validation passed: {result.get('validation_passed')}")
    print(f"Flagged: {result.get('flagged', False)}")
    print(f"Report: {result.get('report_path')}")

if __name__ == "__main__":
    main()
