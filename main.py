"""Beginner project: read a task CSV and count task statuses."""
import csv
from pathlib import Path

INPUT_FILE = Path("data/tasks.csv")
OUTPUT_FILE = Path("output/daily_summary.txt")


def main():
    # Step 1: Make sure the input file exists.
    if not INPUT_FILE.exists():
        print(f"Could not find {INPUT_FILE}. Check that you are in the project folder.")
        return

    # Step 2: Read each row from the CSV file.
    total_tasks = 0
    completed_tasks = 0
    pending_tasks = 0

    with INPUT_FILE.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            total_tasks += 1
            status = row["Status"].strip().lower()

            if status == "completed":
                completed_tasks += 1
            elif status == "pending":
                pending_tasks += 1

    # Step 3: Display the summary.
    summary = (
        "IB OPS DAILY OPERATIONS TASK SUMMARY\n"
        "=============================\n"
        f"Total tasks: {total_tasks}\n"
        f"Completed tasks: {completed_tasks}\n"
        f"Pending tasks: {pending_tasks}\n"
    )

    print(summary)

    # Step 4: Save the same summary to a text file.(Mock Database)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(summary, encoding="utf-8")
    print(f"Summary saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
