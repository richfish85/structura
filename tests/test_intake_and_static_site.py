from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from structura.db import connect, initialize, validate
from structura.intake import (
    IntakeError,
    import_audit,
    import_batch,
    import_context,
    import_normalization,
    import_verification,
)
from structura.static_site import MARKER, render_static_site


ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "research_batches" / "pilot-1998-cpu"
DESKTOP_SCOUT = BATCH / "jobs" / "job-1998-cpu-scout-desktop-server-002" / "runs" / "run-20260908T000519Z-luna-desktop-server-02"
MOBILE_SCOUT = BATCH / "jobs" / "job-1998-cpu-scout-mobile-upgrade-003" / "runs" / "run-20260908T000519Z-luna-mobile-upgrade-03"
OMISSION_VERIFICATION = BATCH / "jobs" / "job-1998-cpu-verify-omissions-004" / "runs" / "run-20260908T001533Z-terra-verifier-04"


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

    def write_context(self) -> tuple[Path, Path, Path]:
        intent = self.temp_root / "intent.csv"
        benchmarks = self.temp_root / "benchmarks.csv"
        sources = self.temp_root / "context-sources.csv"
        intent.write_text(
            "batch_key,candidate_key,claim_scope,problem_addressed,target_user,engineering_response,confidence,source_key,source_locator,evidence_note,limitations,researcher\n"
            "pilot-1998-cpu-gpu-hdd,intel-celeron-300a,manufacturer_stated,Improve affordable Basic PC performance,New and value-PC buyers,Add 128 KB integrated L2 cache,high,intel-celeron-cache-launch,launch section,Intel presents the cached part as a value-PC performance improvement,Manufacturer positioning is not an independent market finding,luna-context-a\n",
            encoding="utf-8",
        )
        benchmarks.write_text(
            "batch_key,candidate_key,comparison_group_key,benchmark_name,metric_name,result_value,result_unit,higher_is_better,system_configuration,test_date,result_provenance,confidence,source_key,source_locator,limitations,researcher\n"
            "pilot-1998-cpu-gpu-hdd,intel-celeron-300a,spec95-mu440ex-aug98,SPEC CPU95,SPECint95,11.3,ratio,true,Intel MU440EX; 64 MB SDRAM; UnixWare 2.0,1998-08,standards_body_vendor_submitted,high,spec-celeron-300a,result summary,Submitted by Intel and compiler-optimized,luna-context-a\n",
            encoding="utf-8",
        )
        sources.write_text(
            "source_key,title,publisher,source_type,source_tier,url,publication_date,accessed_date,scope_note\n"
            "intel-celeron-cache-launch,Intel Introduces Celeron 333 and 300A,Intel,press_release,1,https://www.intel.com/pressroom/archive/releases/1998/dp082498.htm,1998-08-24,2026-09-08,Manufacturer positioning and cache details\n"
            "spec-celeron-300a,SPECint95 Intel MU440EX 300A,SPEC,benchmark_disclosure,1,https://www.spec.org/example-celeron-300a.html,1998-09-15,2026-09-08,Fully disclosed benchmark result\n",
            encoding="utf-8",
        )
        return intent, benchmarks, sources

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

    def test_disjoint_scout_runs_reuse_sources_and_preserve_raw_source_wording(self):
        import_batch(self.db_path, self.candidates, self.sources)
        first = import_batch(self.db_path, DESKTOP_SCOUT / "candidates.csv", DESKTOP_SCOUT / "sources.csv")
        second = import_batch(self.db_path, MOBILE_SCOUT / "candidates.csv", MOBILE_SCOUT / "sources.csv")
        verification = import_verification(self.db_path, OMISSION_VERIFICATION / "verification.csv")
        self.assertEqual(first.candidate_count, 6)
        self.assertEqual(second.candidate_count, 6)
        self.assertEqual(verification.candidate_count, 12)
        self.assertTrue(import_batch(self.db_path, DESKTOP_SCOUT / "candidates.csv", DESKTOP_SCOUT / "sources.csv").already_imported)
        self.assertTrue(import_batch(self.db_path, MOBILE_SCOUT / "candidates.csv", MOBILE_SCOUT / "sources.csv").already_imported)
        self.assertTrue(import_verification(self.db_path, OMISSION_VERIFICATION / "verification.csv").already_imported)
        with connect(self.db_path, read_only=True) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM research_import_runs").fetchone()[0], 4)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM entities").fetchone()[0], 22)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0], 15)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM intake_source_records").fetchone()[0], 19)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM verification_records").fetchone()[0], 12)
            raw_quickref_notes = connection.execute("SELECT COUNT(DISTINCT scope_note_raw) FROM intake_source_records WHERE source_key_raw='intel-quickref-year'").fetchone()[0]
            resolved_quickref = connection.execute("SELECT COUNT(*) FROM sources WHERE source_key='intel-quickref-year'").fetchone()[0]
            self.assertGreaterEqual(raw_quickref_notes, 2)
            self.assertEqual(resolved_quickref, 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM entities WHERE record_status='canonical'").fetchone()[0], 0)
            self.assertEqual(validate(connection), [])

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

    def test_current_normalization_and_audit_import_without_promotion(self):
        import_batch(self.db_path, self.candidates, self.sources)
        import_verification(self.db_path, BATCH / "02_verification.csv")
        normalization = BATCH / "03_normalization_proposal.csv"
        audit = BATCH / "04_audit_findings.csv"
        first_normalization = import_normalization(self.db_path, normalization)
        second_normalization = import_normalization(self.db_path, normalization)
        first_audit = import_audit(self.db_path, audit)
        second_audit = import_audit(self.db_path, audit)
        self.assertEqual(first_normalization.candidate_count, 10)
        self.assertFalse(first_normalization.already_imported)
        self.assertTrue(second_normalization.already_imported)
        self.assertEqual(first_audit.candidate_count, 15)
        self.assertFalse(first_audit.already_imported)
        self.assertTrue(second_audit.already_imported)
        with connect(self.db_path, read_only=True) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM research_import_runs").fetchone()[0], 4)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM normalization_proposals").fetchone()[0], 10)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM normalization_proposals WHERE date_precision='quarter'").fetchone()[0], 2)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM audit_findings").fetchone()[0], 15)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM audit_finding_candidate_refs").fetchone()[0], 11)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM audit_finding_proposed_keys").fetchone()[0], 12)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM entities WHERE record_status='canonical'").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM relationships").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT workflow_status FROM research_batches WHERE batch_key='pilot-1998-cpu-gpu-hdd'").fetchone()[0], "audit")
            self.assertEqual(validate(connection), [])
        output = self.temp_root / "full-review-site"
        render_static_site(self.db_path, output)
        batch_page = (output / "batches" / "pilot-1998-cpu-gpu-hdd.html").read_text(encoding="utf-8")
        amd_page = (output / "candidates" / "amd-k6-2-350.html").read_text(encoding="utf-8")
        self.assertIn("Audit findings and omission leads", batch_page)
        self.assertIn("intel-pentium-ii-333", batch_page)
        self.assertIn("Normalization proposal", amd_page)
        self.assertIn("amd-k6-2-family", amd_page)
        self.assertIn("Audit findings", amd_page)

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

    def test_context_import_is_idempotent_noncanonical_and_rendered(self):
        import_batch(self.db_path, self.candidates, self.sources)
        intent, benchmarks, sources = self.write_context()
        first = import_context(self.db_path, intent, benchmarks, sources)
        second = import_context(self.db_path, intent, benchmarks, sources)
        self.assertFalse(first.already_imported)
        self.assertTrue(second.already_imported)
        self.assertEqual(first.run_key, second.run_key)
        self.assertEqual(first.intent_count, 1)
        self.assertEqual(first.benchmark_count, 1)
        with connect(self.db_path, read_only=True) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM product_intent_claims").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM benchmark_observations").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM context_source_records").fetchone()[0], 2)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM entities WHERE record_status='canonical'").fetchone()[0], 0)
            self.assertEqual(validate(connection), [])
        output = self.temp_root / "context-review-site"
        render_static_site(self.db_path, output)
        candidate_page = (output / "candidates" / "intel-celeron-300a.html").read_text(encoding="utf-8")
        self.assertIn("Why it existed", candidate_page)
        self.assertIn("Improve affordable Basic PC performance", candidate_page)
        self.assertIn("What difference it made", candidate_page)
        self.assertIn("SPECint95", candidate_page)
        self.assertNotIn("<script", candidate_page.lower())

    def test_context_import_rejects_unquoted_extra_columns(self):
        import_batch(self.db_path, self.candidates, self.sources)
        intent, benchmarks, sources = self.write_context()
        intent.write_text(
            "batch_key,candidate_key,claim_scope,problem_addressed,target_user,engineering_response,confidence,source_key,source_locator,evidence_note,limitations,researcher\n"
            "pilot-1998-cpu-gpu-hdd,intel-celeron-300a,manufacturer_stated,Affordable computing,dealers,integrators,Integrated cache,high,intel-celeron-cache-launch,launch,Positioning evidence,Comma is deliberately unquoted,tester\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(IntakeError, "does not have exactly 12 columns"):
            import_context(self.db_path, intent, benchmarks, sources)
        with connect(self.db_path, read_only=True) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM context_import_runs").fetchone()[0], 0)

    def test_context_import_rejects_mixed_comparison_group(self):
        import_batch(self.db_path, self.candidates, self.sources)
        intent, benchmarks, sources = self.write_context()
        benchmarks.write_text(
            benchmarks.read_text(encoding="utf-8")
            + "pilot-1998-cpu-gpu-hdd,intel-celeron-333,spec95-mu440ex-aug98,SPEC CPU95,SPECfp95,9.5,ratio,true,Different system,1998-08,standards_body_vendor_submitted,high,spec-celeron-300a,result summary,Mixed configuration is deliberate,luna-context-a\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(IntakeError, "changes the metric or configuration"):
            import_context(self.db_path, intent, benchmarks, sources)
        with connect(self.db_path, read_only=True) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM context_import_runs").fetchone()[0], 0)

    def test_static_site_refuses_nonempty_foreign_directory(self):
        output = self.temp_root / "not-owned"
        output.mkdir()
        (output / "user-file.txt").write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not owned"):
            render_static_site(self.db_path, output)
        self.assertTrue((output / "user-file.txt").is_file())


if __name__ == "__main__":
    unittest.main()
