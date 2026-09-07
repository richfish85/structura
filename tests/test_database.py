from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from structura.db import connect, counts, initialize, validate


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        initialize(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initializes_schema_and_proposed_ontology(self):
        with connect(self.db_path, read_only=True) as connection:
            migration_count = connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
            type_count = connection.execute("SELECT COUNT(*) FROM entity_types").fetchone()[0]
            predicate_count = connection.execute("SELECT COUNT(*) FROM predicates").fetchone()[0]
            totals = counts(connection)
        self.assertEqual(migration_count, 5)
        self.assertGreaterEqual(type_count, 10)
        self.assertGreaterEqual(predicate_count, 15)
        self.assertEqual(totals["entities"], 0)
        self.assertEqual(totals["research_batches"], 1)

    def test_foreign_keys_reject_unknown_entity_type(self):
        with connect(self.db_path) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO entities(entity_key, name, entity_type_code) VALUES (?, ?, ?)",
                    ("bad-type", "Bad type", "not_a_type"),
                )

    def test_validator_rejects_unsupported_canonical_entity(self):
        with connect(self.db_path) as connection:
            connection.execute(
                "INSERT INTO entities(entity_key, name, entity_type_code, record_status) VALUES (?, ?, ?, ?)",
                ("test-product", "Test product", "product", "canonical"),
            )
            problems = validate(connection)
        self.assertIn("canonical entity has no supporting evidence: test-product", problems)

    def test_validator_accepts_empty_foundation(self):
        with connect(self.db_path, read_only=True) as connection:
            self.assertEqual(validate(connection), [])


if __name__ == "__main__":
    unittest.main()
