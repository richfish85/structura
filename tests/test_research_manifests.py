from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "research_batches" / "templates"


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


if __name__ == "__main__":
    unittest.main()
