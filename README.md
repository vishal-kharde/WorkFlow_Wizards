# IB Ops Data Processing & Reconciliation Automation

A beginner-friendly four-week internship project demonstrating how Python can automate repetitive operations data processing using synthetic CSV data.

## Features
- Reads a CSV using pandas
- Cleans whitespace and normalizes known status/priority values
- Validates required fields, dates, status, priority and numeric amounts
- Rejects invalid records with explanations
- Loads valid records into a SQLite database
- Prevents duplicate task IDs from being inserted twice
- Creates an audit table and a log file
- Generates an exception CSV and a summary report
- Includes automated unit tests and a data mapping document

## Quick start
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Read `docs/setup_guide.md` for detailed setup instructions.

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Project structure
```text
ib_ops_automation_project/
├── main.py
├── src/
│   ├── __init__.py
│   └── ops_automation.py
├── data/
│   └── sample_tasks.csv
├── output/                 # generated database and reports
├── logs/                   # generated processing log
├── tests/
│   └── test_pipeline.py
├── docs/
│   ├── data_mapping.md
│   ├── setup_guide.md
│   └── final_presentation_outline.md
└── requirements.txt
```

## Four-week learning plan
- Week 1: Set up Python, inspect the sample file, run a basic script and explain the workflow.
- Week 2: Document the mapping, clean data, and explain validation rules.
- Week 3: Load data to SQLite, add logging, exception reports and tests.
- Week 4: Run edge-case tests, document results, demonstrate the workflow and present measured impact.

## Demo caveats
The sample file deliberately contains invalid rows. The pipeline should reject those rows and explain why. The first run creates the database; a second run skips task IDs already stored in the database.

This is an educational prototype. Use only synthetic data. Do not connect it to bank systems or use confidential or customer information.
