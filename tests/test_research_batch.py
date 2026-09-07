from __future__ import annotations

import csv
import unittest
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "research_batches" / "pilot-1998-cpu"


class ResearchBatchTests(unittest.TestCase):
    def test_scout_batch_has_ten_unique_candidates(self):
        with (BATCH / "01_scout_candidates.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        keys = [row["candidate_key"] for row in rows]
        self.assertEqual(len(rows), 10)
        self.assertEqual(len(keys), len(set(keys)))
        self.assertTrue(all(row["batch_key"] == "pilot-1998-cpu-gpu-hdd" for row in rows))
        self.assertTrue(all(row["source_1_url"] for row in rows))

    def test_scout_sources_are_registered_primary_origins(self):
        with (BATCH / "01_sources.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["source_tier"] == "1" for row in rows))
        allowed_hosts = {"www.intel.com", "ir.amd.com"}
        self.assertTrue(all(urlparse(row["url"]).hostname in allowed_hosts for row in rows))
        self.assertTrue(all(row["accessed_date"] == "2026-09-08" for row in rows))

    def test_batch_remains_before_verification_gate(self):
        status = (BATCH / "00_STATUS.md").read_text(encoding="utf-8")
        self.assertIn("scouting complete; verification not started", status)
        self.assertIn("[ ] Independent verification", status)
        self.assertIn("[ ] Canonical import", status)


if __name__ == "__main__":
    unittest.main()
