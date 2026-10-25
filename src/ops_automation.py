"""Core pipeline: extract, clean, validate, persist, audit and report."""
from __future__ import annotations

import logging
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

import pandas as pd

REQUIRED_COLUMNS = [
    "task_id", "trade_date", "team", "task_type", "status",
    "priority", "owner", "amount_usd", "notes"
]
ALLOWED_STATUSES = {"New", "In Progress", "Completed", "On Hold"}
ALLOWED_PRIORITIES = {"Low", "Medium", "High", "Critical"}
DATE_FORMAT = "%Y-%m-%d"


def configure_logging(log_dir: Path) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "processing.log"
    logger = logging.getLogger("ib_ops_automation")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    return log_path


def clean_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def validate_and_clean(input_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (valid records, rejected records with a reason)."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    df.columns = [str(c).strip().lower() for c in df.columns]

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Input file is missing required columns: {', '.join(missing_columns)}")

    df = df[REQUIRED_COLUMNS].copy()
    for col in ["task_id", "trade_date", "team", "task_type", "status", "priority", "owner", "notes"]:
        df[col] = df[col].map(clean_text)

    # Normalize known categorical fields without accepting arbitrary values.
    status_map = {s.lower(): s for s in ALLOWED_STATUSES}
    priority_map = {s.lower(): s for s in ALLOWED_PRIORITIES}
    df["status"] = df["status"].map(lambda x: status_map.get(x.lower(), x))
    df["priority"] = df["priority"].map(lambda x: priority_map.get(x.lower(), x))

    errors: list[str] = []
    seen_ids: set[str] = set()
    valid_indices: list[int] = []
    rejected_rows: list[dict[str, Any]] = []

    for idx, row in df.iterrows():
        row_errors = []
        task_id = row["task_id"]

        if not task_id:
            row_errors.append("Missing task_id")
        elif task_id in seen_ids:
            row_errors.append("Duplicate task_id in input file")
        else:
            seen_ids.add(task_id)

        for field in ["trade_date", "team", "task_type", "status", "priority", "owner"]:
            if not row[field]:
                row_errors.append(f"Missing {field}")

        if row["trade_date"]:
            try:
                parsed_date = datetime.strptime(row["trade_date"], DATE_FORMAT)
                if parsed_date.strftime(DATE_FORMAT) != row["trade_date"]:
                    row_errors.append("trade_date must use YYYY-MM-DD")
            except ValueError:
                row_errors.append("Invalid trade_date; expected YYYY-MM-DD")

        if row["status"] and row["status"] not in ALLOWED_STATUSES:
            row_errors.append(f"Invalid status: {row['status']}")
        if row["priority"] and row["priority"] not in ALLOWED_PRIORITIES:
            row_errors.append(f"Invalid priority: {row['priority']}")

        try:
            amount = float(row["amount_usd"])
            if amount < 0:
                row_errors.append("amount_usd cannot be negative")
        except (TypeError, ValueError):
            amount = None
            row_errors.append("amount_usd must be a number")

        if row_errors:
            rejected = row.to_dict()
            rejected["error_reason"] = "; ".join(row_errors)
            rejected_rows.append(rejected)
        else:
            valid_indices.append(idx)
            df.at[idx, "amount_usd"] = amount

    valid = df.loc[valid_indices].copy()
    if not valid.empty:
        valid["amount_usd"] = valid["amount_usd"].astype(float)
    rejected = pd.DataFrame(rejected_rows, columns=REQUIRED_COLUMNS + ["error_reason"])
    return valid, rejected


def initialize_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ops_tasks (
                task_id TEXT PRIMARY KEY,
                trade_date TEXT NOT NULL,
                team TEXT NOT NULL,
                task_type TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                owner TEXT NOT NULL,
                amount_usd REAL NOT NULL CHECK(amount_usd >= 0),
                notes TEXT,
                created_at_utc TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processing_audit (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                outcome TEXT NOT NULL,
                details TEXT NOT NULL,
                processed_at_utc TEXT NOT NULL
            )
        """)
        conn.commit()


def load_records(valid: pd.DataFrame, db_path: Path, logger: logging.Logger) -> tuple[int, int]:
    inserted = 0
    database_duplicates = 0
    timestamp = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        for _, row in valid.iterrows():
            try:
                conn.execute("""
                    INSERT INTO ops_tasks
                    (task_id, trade_date, team, task_type, status, priority, owner,
                     amount_usd, notes, created_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row["task_id"], row["trade_date"], row["team"], row["task_type"],
                    row["status"], row["priority"], row["owner"], float(row["amount_usd"]),
                    row["notes"], timestamp
                ))
                conn.execute(
                    "INSERT INTO processing_audit (task_id, outcome, details, processed_at_utc) VALUES (?, ?, ?, ?)",
                    (row["task_id"], "INSERTED", "Record loaded successfully", timestamp)
                )
                inserted += 1
                logger.info("INSERTED task_id=%s", row["task_id"])
            except sqlite3.IntegrityError:
                database_duplicates += 1
                conn.execute(
                    "INSERT INTO processing_audit (task_id, outcome, details, processed_at_utc) VALUES (?, ?, ?, ?)",
                    (row["task_id"], "SKIPPED", "task_id already exists in database", timestamp)
                )
                logger.warning("SKIPPED existing task_id=%s", row["task_id"])
        conn.commit()
    return inserted, database_duplicates


def run_pipeline(input_path: Path, db_path: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = configure_logging(output_dir.parent / "logs")
    logger = logging.getLogger("ib_ops_automation")
    start = time.perf_counter()
    logger.info("Pipeline started input=%s", input_path)

    valid, rejected = validate_and_clean(input_path)
    initialize_database(db_path)
    inserted, database_duplicates = load_records(valid, db_path, logger)

    exceptions_path = output_dir / "exceptions.csv"
    rejected.to_csv(exceptions_path, index=False)

    with sqlite3.connect(db_path) as conn:
        total_in_db = conn.execute("SELECT COUNT(*) FROM ops_tasks").fetchone()[0]
        status_rows = conn.execute(
            "SELECT status, COUNT(*) FROM ops_tasks GROUP BY status ORDER BY status"
        ).fetchall()
        total_value = conn.execute("SELECT COALESCE(SUM(amount_usd), 0) FROM ops_tasks").fetchone()[0]

    elapsed = round(time.perf_counter() - start, 3)
    summary = {
        "input_file": str(input_path),
        "input_records": len(valid) + len(rejected),
        "valid_records": len(valid),
        "rejected_records": len(rejected),
        "inserted_this_run": inserted,
        "already_in_database": database_duplicates,
        "total_tasks_in_database": total_in_db,
        "total_amount_usd_in_database": round(float(total_value), 2),
        "processing_seconds": elapsed,
        "database": str(db_path),
        "exceptions_file": str(exceptions_path),
        "log_file": str(log_path),
    }

    report_path = output_dir / "summary_report.txt"
    with report_path.open("w", encoding="utf-8") as f:
        f.write("IB OPS DATA PROCESSING SUMMARY\n")
        f.write("=" * 32 + "\n")
        for key, value in summary.items():
            f.write(f"{key.replace('_', ' ').title()}: {value}\n")
        f.write("\nDatabase status breakdown:\n")
        for status, count in status_rows:
            f.write(f"- {status}: {count}\n")

    logger.info("Pipeline completed summary=%s", summary)
    return summary
