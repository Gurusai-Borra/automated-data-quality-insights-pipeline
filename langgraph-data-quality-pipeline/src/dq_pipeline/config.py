from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "sample_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
LOG_DIR = PROJECT_ROOT / "logs"

REQUIRED_COLUMNS = ["customer_id", "age", "email", "monthly_spend"]
NUMERIC_COLUMNS = ["age", "monthly_spend"]
MAX_VALIDATION_RETRIES = 1
