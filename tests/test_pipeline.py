import tempfile
import unittest
from pathlib import Path

from src.ops_automation import validate_and_clean, initialize_database, load_records
import logging


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.csv_path = self.root / "tasks.csv"
        self.csv_path.write_text(
            "task_id,trade_date,team,task_type,status,priority,owner,amount_usd,notes\n"
            "T-1,2026-10-20,Ops,Check,New,High,Sam,100,Valid\n"
            "T-2,2026-10-20,Ops,Check,BadStatus,High,Sam,100,Invalid status\n"
            "T-3,2026-10-20,Ops,Check,New,High,Sam,nope,Invalid amount\n",
            encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_validation_separates_valid_and_rejected(self):
        valid, rejected = validate_and_clean(self.csv_path)
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(rejected), 2)
        self.assertEqual(valid.iloc[0]["task_id"], "T-1")

    def test_database_load_is_idempotent_for_existing_id(self):
        valid, _ = validate_and_clean(self.csv_path)
        db = self.root / "test.db"
        initialize_database(db)
        logger = logging.getLogger("test")
        inserted1, duplicates1 = load_records(valid, db, logger)
        inserted2, duplicates2 = load_records(valid, db, logger)
        self.assertEqual((inserted1, duplicates1), (1, 0))
        self.assertEqual((inserted2, duplicates2), (0, 1))


if __name__ == "__main__":
    unittest.main()
