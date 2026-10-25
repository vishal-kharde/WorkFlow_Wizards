# Setup Guide (Windows + IntelliJ IDEA)

## Tools
- Python 3.11 or newer
- IntelliJ IDEA with the Python plugin (where supported by your edition)
- Terminal / PowerShell
- `pip` for installing dependencies
- SQLite database (built into Python; no separate server required)

## 1. Open the project
Extract the ZIP file and open the `ib_ops_automation_project` folder in IntelliJ IDEA.

## 2. Configure Python
Install Python from https://www.python.org/downloads/ and enable **Add Python to PATH** during installation.
In IntelliJ, install/enable the Python plugin if your edition supports it, then select the project Python interpreter.

## 3. Create a virtual environment
Open the terminal in the project folder:

```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt and run:
```bat
.venv\\Scripts\\activate.bat
```

## 4. Run the project
```powershell
python main.py
```

Expected result: a console summary plus these generated files:
- `output/ib_ops.db` — SQLite database
- `output/exceptions.csv` — invalid rows and reasons
- `output/summary_report.txt` — processing summary
- `logs/processing.log` — processing events

To use another file:
```powershell
python main.py --input data/my_tasks.csv --db output/ib_ops.db --output-dir output
```

## 5. Verify database contents
Run this short Python command from the project folder:
```powershell
python -c "import sqlite3; c=sqlite3.connect('output/ib_ops.db'); print(c.execute('SELECT task_id,status,owner FROM ops_tasks').fetchall()); c.close()"
```

## 6. Reset for a clean demo
Stop the script, then delete `output/ib_ops.db` and the generated files in `output/` and `logs/`. Keep the source CSV intact.
