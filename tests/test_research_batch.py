from __future__ import annotations

import csv
import unittest
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "research_batches" / "pilot-1998-cpu"
PILOT = ROOT / "research_batches" / "pilot-1998"


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

    def test_batch_remains_before_canonical_gate(self):
        status = (BATCH / "00_STATUS.md").read_text(encoding="utf-8")
        self.assertIn("22 candidates scouted, independently verified, normalized", status)
        self.assertIn("[x] Independent verification", status)
        self.assertIn("[x] Normalization proposal", status)
        self.assertIn("[x] Omission and duplicate audit", status)
        self.assertIn("[x] Mobile and upgrade segment boundary decision", status)
        self.assertIn("[x] Purpose and benchmark context", status)
        self.assertIn("[x] Post-expansion audit", status)
        self.assertIn("[x] Initial human review and discrepancy disposition", status)
        self.assertIn("[ ] Canonical import", status)

    def test_owner_review_decisions_retain_named_discrepancies(self):
        rows = []
        for name in (
            "02_REVIEW_DECISIONS_CPU.csv",
            "03_REVIEW_DECISIONS_GPU.csv",
            "04_REVIEW_DECISIONS_HDD.csv",
        ):
            with (PILOT / name).open(encoding="utf-8", newline="") as handle:
                rows.extend(csv.DictReader(handle))

        levels = {row["candidate_key"]: row["discrepancy_level"] for row in rows}
        self.assertEqual(
            levels,
            {
                "intel-pentium-ii-overdrive-300": "L3",
                "intel-pentium-ii-overdrive-333": "L3",
                "intel-pentium-ii-xeon-450": "L3",
                "intel-i740": "L2",
                "matrox-mga-g200": "L3",
                "ati-rage-128-gl": "L4",
                "ati-rage-128-vr": "L4",
                "3dfx-voodoo-banshee": "L2",
                "quantum-fireball-el": "L2",
            },
        )
        self.assertTrue(all(row["disposition"] == "retain_for_review" for row in rows))
        self.assertTrue(all(row["resolving_evidence"] for row in rows))


if __name__ == "__main__":
    unittest.main()
