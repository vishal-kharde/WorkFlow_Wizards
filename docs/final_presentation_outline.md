# Final Presentation (5–7 minutes)

## Slide 1 — Title
IB Ops Data Processing & Reconciliation Automation
Student name, mentor, internship dates

## Slide 2 — The business problem
Manual spreadsheet checking and data entry can be repetitive, inconsistent and difficult to audit.

## Slide 3 — Proposed solution
CSV input → validation and cleaning → SQLite database → audit log → summary and exceptions report.

## Slide 4 — Technical design
Python, pandas, SQLite, logging, CSV reports and automated tests.

## Slide 5 — Demonstration
1. Show the sample CSV and point out intentionally invalid rows.
2. Run `python main.py`.
3. Open `output/exceptions.csv`.
4. Open `output/summary_report.txt`.
5. Query the database and show valid rows.
6. Run it again to demonstrate duplicate protection.

## Slide 6 — Results
Report actual counts from your run: input rows, valid rows, rejected rows, inserted rows and processing time. Do not claim time savings unless measured against a documented manual baseline.

## Slide 7 — Lessons and next steps
Data quality, exception handling, auditability, testing, and possible future additions such as Excel support, a simple dashboard, email alerts or a controlled review workflow.
