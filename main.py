"""Command-line entry point for the IB Ops Data Processing Automation project."""
import argparse
from pathlib import Path
from src.ops_automation import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Validate an IB Ops CSV and load valid tasks into SQLite.")
    parser.add_argument("--input", default="data/sample_tasks.csv", help="Path to input CSV file")
    parser.add_argument("--db", default="output/ib_ops.db", help="Path to SQLite database")
    parser.add_argument("--output-dir", default="output", help="Directory for reports and exception files")
    args = parser.parse_args()

    summary = run_pipeline(
        input_path=Path(args.input),
        db_path=Path(args.db),
        output_dir=Path(args.output_dir),
    )
    print("\n=== IB Ops Automation Summary ===")
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    main()
