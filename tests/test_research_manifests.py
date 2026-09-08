from __future__ import annotations

import json
import hashlib
import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "research_batches" / "templates"
PILOT_JOBS = ROOT / "research_batches" / "pilot-1998-cpu" / "jobs"


class ResearchManifestTests(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((TEMPLATES / name).read_text(encoding="utf-8"))

    def test_job_template_blocks_canonical_promotion(self):
        manifest = self.load("job_manifest.template.json")
        self.assertEqual(manifest["manifest_type"], "job")
        self.assertIn(manifest["stage"], {"scout", "verifier", "normalizer", "auditor"})
        self.assertFalse(manifest["handoff"]["canonical_promotion_allowed"])
        self.assertTrue(manifest["scope"]["stopping_rule"])
        self.assertTrue(manifest["retry_policy"]["input_snapshot_sha256"])

    def test_result_template_records_worker_and_artifact_identity(self):
        manifest = self.load("result_manifest.template.json")
        self.assertEqual(manifest["manifest_type"], "result")
        self.assertEqual(manifest["status"], "submitted")
        self.assertTrue(manifest["run_id"])
        self.assertTrue(manifest["artifact_id"])
        self.assertTrue(manifest["worker"]["agent_id"])
        self.assertFalse(manifest["quality"]["canonical_sql_written"])

    def test_dispatched_omission_scout_jobs_are_disjoint_and_inputs_match(self):
        paths = sorted(PILOT_JOBS.glob("job-1998-cpu-scout-*/job_manifest.json"))
        self.assertEqual(len(paths), 2)
        assigned: set[str] = set()
        for path in paths:
            manifest = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["stage"], "scout")
            self.assertFalse(manifest["handoff"]["canonical_promotion_allowed"])
            keys = set(manifest["scope"]["record_keys"])
            self.assertTrue(keys)
            self.assertTrue(assigned.isdisjoint(keys))
            assigned.update(keys)
            for item in manifest["inputs"]:
                input_path = (path.parent / item["path"]).resolve()
                self.assertTrue(input_path.is_file())
                self.assertEqual(hashlib.sha256(input_path.read_bytes()).hexdigest(), item["sha256"])
        self.assertEqual(len(assigned), 12)

    def test_accepted_scout_results_match_manifests_and_output_hashes(self):
        jobs = sorted(PILOT_JOBS.glob("job-1998-cpu-scout-*/job_manifest.json"))
        workers: set[str] = set()
        for job_path in jobs:
            job = json.loads(job_path.read_text(encoding="utf-8"))
            self.assertEqual(job["status"], "accepted")
            run_path = job_path.parent / "runs" / job["accepted_result"]["run_id"]
            result = json.loads((run_path / "result_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(result["artifact_id"], job["accepted_result"]["artifact_id"])
            self.assertEqual(result["status"], "submitted")
            self.assertFalse(result["quality"]["canonical_sql_written"])
            workers.add(result["worker"]["agent_id"])
            for output in result["outputs"]:
                output_path = run_path / output["path"]
                self.assertEqual(hashlib.sha256(output_path.read_bytes()).hexdigest(), output["sha256"])
                if output_path.suffix == ".csv":
                    with output_path.open(encoding="utf-8", newline="") as handle:
                        self.assertEqual(sum(1 for _ in csv.DictReader(handle)), output["row_count"])
        self.assertEqual(len(workers), 2)

    def test_independent_verifier_result_matches_frozen_scout_inputs(self):
        job_path = PILOT_JOBS / "job-1998-cpu-verify-omissions-004" / "job_manifest.json"
        job = json.loads(job_path.read_text(encoding="utf-8"))
        self.assertEqual(job["status"], "accepted")
        run_path = job_path.parent / "runs" / job["accepted_result"]["run_id"]
        result = json.loads((run_path / "result_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(result["artifact_id"], job["accepted_result"]["artifact_id"])
        self.assertEqual(result["worker"]["capability_route"], "terra")
        scout_workers = {
            json.loads(path.read_text(encoding="utf-8"))["owner"]["agent_id"]
            for path in PILOT_JOBS.glob("job-1998-cpu-scout-*/job_manifest.json")
        }
        self.assertNotIn(result["worker"]["agent_id"], scout_workers)
        self.assertFalse(result["quality"]["self_approval_violation"])
        job_inputs = {item["artifact_id"]: item["sha256"] for item in job["inputs"]}
        self.assertEqual(job_inputs, {item["artifact_id"]: item["sha256"] for item in result["inputs"]})
        for output in result["outputs"]:
            output_path = run_path / output["path"]
            self.assertEqual(hashlib.sha256(output_path.read_bytes()).hexdigest(), output["sha256"])
        with (run_path / "verification.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 12)
        self.assertEqual({row["candidate_key"] for row in rows}, set(job["scope"]["record_keys"]))


if __name__ == "__main__":
    unittest.main()
