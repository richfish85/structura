from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from structura.db import initialize
from structura.web import create_app, safe_external_url


def request(app, path: str):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    if "?" in path:
        path_info, query = path.split("?", 1)
    else:
        path_info, query = path, ""
    body = b"".join(app({"PATH_INFO": path_info, "QUERY_STRING": query}, start_response))
    return captured["status"], captured["headers"], body


class WebTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        initialize(self.db_path)
        self.app = create_app(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_home_renders_foundation_status(self):
        status, headers, body = request(self.app, "/")
        self.assertEqual(status, "200 OK")
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn("default-src 'none'", headers["Content-Security-Policy"])
        self.assertIn(b"1998 CPU, GPU, and HDD", body)
        self.assertIn(b"Local foundation", body)

    def test_health_returns_counts(self):
        status, headers, body = request(self.app, "/health")
        payload = json.loads(body)
        self.assertEqual(status, "200 OK")
        self.assertIn("application/json", headers["Content-Type"])
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["counts"]["entities"], 0)

    def test_entities_handles_empty_database(self):
        status, _, body = request(self.app, "/entities?q=ssd")
        self.assertEqual(status, "200 OK")
        self.assertIn(b"No matching entities", body)

    def test_external_links_allow_only_http_and_https(self):
        self.assertEqual(safe_external_url("https://example.com/manual"), "https://example.com/manual")
        self.assertIsNone(safe_external_url("javascript:alert(1)"))
        self.assertIsNone(safe_external_url("file:///local/secret"))


if __name__ == "__main__":
    unittest.main()
