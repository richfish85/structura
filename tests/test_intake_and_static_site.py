from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from structura.db import connect, initialize, validate
from structura.intake import IntakeError, import_batch, import_verification
from structura.static_site import MARKER, render_static_site


ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "research_batches" / "pilot-1998-cpu"


class IntakeAndStaticSiteTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_root = Path(self.temp_dir.name)
        self.db_path = self.temp_root / "review.db"
        initialize(self.db_path)
        self.candidates = BATCH / "01_scout_candidates.csv"
        self.sources = BATCH / "01_sources.csv"

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_verification(self, path: Path, candidate_key: str = "intel-pentium-ii-350") -> None:
        path.write_text(
            "batch_key,candidate_key,identity_status,manufacturer_status,category_status,release_timing_status,confidence,source_key,source_tier,evidence_role,locator,evidence_note,conflict_note,verifier\n"
            f"pilot-1998-cpu-gpu-hdd,{candidate_key},verified,verified,uncertain,verified,medium,intel-1998-dp041598,1,supports,release paragraph,Independent check notes the named processor variant,,terra-verifier-a\n",
            encoding="utf-8",
        )

    def test_import_is_noncanonical_and_idempotent(self):
        first = import_batch(self.db_path, self.candidates, self.sources, stage="scouting")
        second = import_batch(self.db_path, self.candidates, self.sources, stage="scouting")
        self.assertFalse(first.already_imported)
        self.assertTrue(second.already_imported)
        self.assertEqual(first.run_key, second.run_key)
        with connect(self.db_path, read_only=True) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM research_import_runs").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM intake_candidate_records").fetchone()[0], 10)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM entities WHERE record_status='canonical'").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM entity_evidence WHERE evidence_role='lead_only'").fetchone()[0], 19)
            self.assertEqual(validate(connection), [])

    def test_import_rejects_unregistered_candidate_source(self):
        candidate_copy = self.temp_root / "candidates.csv"
        with self.candidates.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["source_1_url"] = "https://example.com/not-registered"
        with candidate_copy.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaisesRegex(IntakeError, "absent from source file"):
            import_batch(self.db_path, candidate_copy, self.sources)
        with connect(self.db_path, read_only=True) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM research_import_runs").fetchone()[0], 0)

    def test_import_rejects_existing_candidate_key_in_changed_input(self):
        import_batch(self.db_path, self.candidates, self.sources)
        candidate_copy = self.temp_root / "changed.csv"
        source_text = self.candidates.read_text(encoding="utf-8")
        candidate_copy.write_text(source_text.replace("Manufacturer wording identifies", "Different raw observation identifies", 1), encoding="utf-8")
        with self.assertRaisesRegex(IntakeError, "require a human merge decision"):
            import_batch(self.db_path, candidate_copy, self.sources)

    def test_verification_is_idempotent_and_does_not_promote_candidate(self):
        import_batch(self.db_path, self.candidates, self.sources)
        verification = self.temp_root / "verification.csv"
        self.write_verification(verification)
        first = import_verification(self.db_path, verification)
        second = import_verification(self.db_path, verification)
        self.assertFalse(first.already_imported)
        self.assertTrue(second.already_imported)
        with connect(self.db_path, read_only=True) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM verification_records").fetchone()[0], 1)
            status = connection.execute("SELECT record_status FROM entities WHERE entity_key='intel-pentium-ii-350'").fetchone()[0]
            self.assertEqual(status, "candidate")
            self.assertEqual(connection.execute("SELECT workflow_status FROM research_batches WHERE batch_key='pilot-1998-cpu-gpu-hdd'").fetchone()[0], "verification")

    def test_verification_rejects_unknown_candidate_without_writing(self):
        import_batch(self.db_path, self.candidates, self.sources)
        verification = self.temp_root / "unknown-verification.csv"
        self.write_verification(verification, "unknown-product")
        with self.assertRaisesRegex(IntakeError, "not staged"):
            import_verification(self.db_path, verification)
        with connect(self.db_path, read_only=True) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM verification_records").fetchone()[0], 0)

    def test_current_ten_candidate_verification_report_imports_without_promotion(self):
        import_batch(self.db_path, self.candidates, self.sources)
        verification = BATCH / "02_verification.csv"
        first = import_verification(self.db_path, verification)
        second = import_verification(self.db_path, verification)
        self.assertEqual(first.candidate_count, 10)
        self.assertFalse(first.already_imported)
        self.assertTrue(second.already_imported)
        with connect(self.db_path, read_only=True) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM verification_report_records").fetchone()[0], 10)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM verification_evidence_references").fetchone()[0], 20)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM entities WHERE record_status='candidate'").fetchone()[0], 10)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM entities WHERE record_status='canonical'").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM relationships").fetchone()[0], 0)
            self.assertEqual(validate(connection), [])

    def test_static_site_is_plain_deterministic_and_keeps_provenance(self):
        result = import_batch(self.db_path, self.candidates, self.sources)
        verification = self.temp_root / "verification.csv"
        self.write_verification(verification)
        verification_result = import_verification(self.db_path, verification)
        output = self.temp_root / "review-site"
        render_static_site(self.db_path, output)
        first_index = (output / "index.html").read_bytes()
        render_static_site(self.db_path, output)
        self.assertEqual(first_index, (output / "index.html").read_bytes())
        self.assertTrue((output / MARKER).is_file())
        self.assertIn(b"static review export", first_index)
        self.assertNotIn(b"<script", first_index.lower())
        run_page = (output / "runs" / f"{result.run_key}.html").read_text(encoding="utf-8")
        candidate_page = (output / "candidates" / "intel-pentium-ii-350.html").read_text(encoding="utf-8")
        self.assertIn(result.run_key, run_page)
        self.assertIn("Input digest", run_page)
        self.assertNotIn(str(BATCH.resolve()), run_page)
        self.assertIn("<td>2</td><td>10</td>", first_index.decode("utf-8"))
        self.assertIn("Raw hand-off", candidate_page)
        self.assertIn("lead_only", candidate_page)
        self.assertIn("Verification assertions", candidate_page)
        self.assertIn(verification_result.run_key, candidate_page)

    def test_static_site_refuses_nonempty_foreign_directory(self):
        output = self.temp_root / "not-owned"
        output.mkdir()
        (output / "user-file.txt").write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not owned"):
            render_static_site(self.db_path, output)
        self.assertTrue((output / "user-file.txt").is_file())


if __name__ == "__main__":
    unittest.main()
