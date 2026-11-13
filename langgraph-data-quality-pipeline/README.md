# Automated Data Quality & Insights Pipeline using LangGraph

A portfolio-ready Python project that ingests a CSV file, cleans data, validates quality rules, detects numeric outliers, creates charts, and generates a plain-language insights report. LangGraph orchestrates the workflow and conditionally routes invalid data through a bounded retry path before flagging remaining issues.

## Features

- **LangGraph workflow:** ingestion → cleaning → validation → conditional retry/flagging → anomaly detection → report generation.
- **Reusable modules:** separate ingestion, transformation, validation, anomaly detection, visualization, and reporting modules.
- **Data quality metrics:** missing values, duplicate rows, invalid values, validation status, retry count, and anomaly counts.
- **LLM-assisted summary:** optional OpenAI-compatible LLM summary; a deterministic local summary is used when no API key is configured.
- **Charts:** numeric distributions and outlier counts saved as PNG files.
- **Observability:** timestamped run logs and a JSON metrics file.
- **Tests:** pytest coverage for core transformations and validation behavior.

## Repository structure

```text
langgraph-data-quality-pipeline/
├── data/
│   └── sample_data.csv
├── outputs/                  # generated reports, charts and metrics
├── logs/                     # generated run logs
├── src/
│   └── dq_pipeline/
│       ├── __init__.py
│       ├── graph.py
│       ├── nodes.py
│       ├── ingestion.py
│       ├── cleaning.py
│       ├── validation.py
│       ├── anomalies.py
│       ├── visualization.py
│       ├── summarization.py
│       └── config.py
├── tests/
│   ├── test_cleaning.py
│   └── test_validation.py
├── .env.example
├── .gitignore
├── requirements.txt
└── main.py
```

## 1. Set up

Python 3.10+ is recommended.

```bash
git clone https://github.com/<your-username>/langgraph-data-quality-pipeline.git
cd langgraph-data-quality-pipeline

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## 2. Configure the optional LLM

Copy `.env.example` to `.env` and add your key if you want LLM-generated recommendations.

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

The pipeline still runs without an API key. In that case, it generates a rule-based summary. **Never commit `.env` or API keys to GitHub.**

## 3. Run the pipeline

```bash
python main.py
```

By default, the project reads `data/sample_data.csv`. Generated files are written to:

- `outputs/cleaned_data.csv`
- `outputs/quality_report.md`
- `outputs/quality_metrics.json`
- `outputs/missing_values.png`
- `outputs/numeric_outliers.png`
- `logs/pipeline.log`

To use another CSV:

```bash
python main.py --input path/to/your_file.csv
```

## 4. Run tests

```bash
pytest -q
```

## Validation and routing logic

The example schema expects `customer_id`, `age`, `email`, and `monthly_spend`.

- `customer_id` must be present and unique.
- `age` must be numeric and between 0 and 120.
- `email` must contain `@`.
- `monthly_spend` must be numeric and non-negative.

The cleaning step standardizes column names, removes exact duplicate rows, trims text, and coerces expected numeric columns. If validation fails, LangGraph routes back through cleaning once. If it still fails, the run is marked as flagged and continues so the report can explain the outstanding issues. This is a bounded retry, preventing infinite loops.

## Customize for your own dataset

1. Update `REQUIRED_COLUMNS` and `NUMERIC_COLUMNS` in `src/dq_pipeline/config.py`.
2. Add or edit business rules in `src/dq_pipeline/validation.py`.
3. Adjust the IQR multiplier in `src/dq_pipeline/anomalies.py`.
4. Replace the sample CSV with your own data (do not commit sensitive or personal data).

## Architecture

```text
CSV
 │
 ▼
[Ingest]
 │
 ▼
[Clean] ◄──────────────┐
 │                     │ retry (max 1)
 ▼                     │
[Validate] ── invalid ─┘
 │ valid / retry limit reached
 ▼
[Detect anomalies]
 │
 ▼
[Generate charts + LLM/rule-based insights]
 │
 ▼
[Save report, metrics and logs]
```

## Notes

- IQR-based anomaly detection is a simple baseline, not a universal definition of anomalous behavior.
- The sample rules are illustrative; adapt them to the meaning and constraints of your data.
- The LLM receives aggregate findings rather than full row-level records, reducing unnecessary data exposure.
