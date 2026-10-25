# Daily Task Summary

A small Python program that reads a list of tasks from a spreadsheet (CSV file),
counts how many are **Completed** and how many are **Pending**, and saves a
summary to a text file.

You don't need to install anything extra. Python comes with everything this
program needs.

---

## What You Need

| Item | Details |
|------|---------|
| A computer | Windows, Mac, or Linux |
| Python | Version 3.6 or newer (free from python.org) |
| Internet | Only to download Python the first time |

---

## Step-by-Step: How to Run It

| Step | What to Do |
|------|------------|
| 1 | Install Python from **python.org** if you don't have it. During install, tick the box **"Add Python to PATH"**. |
| 2 | Open a **terminal** (Windows: *Command Prompt* / Mac: *Terminal*). |
| 3 | Go into the project folder. Example: `cd Desktop\my-project` |
| 4 | Create the folder `data` inside the project, and put your **`tasks.csv`** file inside it. |
| 5 | Type this and press Enter: `python main.py` |
| 6 | You will see the summary printed on screen, and a file called **`output/daily_summary.txt`** will appear. |

> If `python` doesn't work, try `python3 main.py`.

---

## What the Program Reads (Input)

You give it **one file**: `data/tasks.csv`

| Thing | Rule |
|-------|------|
| File name | Must be called `tasks.csv` |
| Folder | Must be inside a folder called `data` |
| Format | A normal spreadsheet saved as **CSV** (File → Save As → CSV in Excel) |
| Must have a column named | `Status` |
| Status values allowed | `Completed` or `Pending` (capital letters don't matter) |

**Example of what your `tasks.csv` should look like:**

```csv
Task,Owner,Status
Review reports,Alice,Completed
Update inventory,Bob,Pending
Call supplier,Carol,Completed
Fix printer,Dan,Pending