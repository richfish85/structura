from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = PROJECT_ROOT / "data" / "structura.db"
SCHEMA_DIR = PROJECT_ROOT / "schema"


@contextmanager
def connect(
    db_path: Path | str = DEFAULT_DB, *, read_only: bool = False
) -> Iterator[sqlite3.Connection]:
    path = Path(db_path).resolve()
    if read_only:
        connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        if not read_only:
            connection.commit()
    except Exception:
        if not read_only:
            connection.rollback()
        raise
    finally:
        connection.close()


def initialize(db_path: Path | str = DEFAULT_DB) -> Path:
    path = Path(db_path).resolve()
    with connect(path) as connection:
        for migration in sorted(SCHEMA_DIR.glob("*.sql")):
            connection.executescript(migration.read_text(encoding="utf-8"))
    return path


def counts(connection: sqlite3.Connection) -> dict[str, int]:
    names = ("entities", "relationships", "sources", "research_batches")
    return {
        name: int(connection.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0])
        for name in names
    }


def validate(connection: sqlite3.Connection) -> list[str]:
    problems: list[str] = []

    foreign_key_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
    problems.extend(
        f"foreign key failure in {row['table']} row {row['rowid']}"
        for row in foreign_key_rows
    )

    unsupported_entities = connection.execute(
        """
        SELECT entity_key
        FROM entities e
        WHERE e.record_status = 'canonical'
          AND NOT EXISTS (
              SELECT 1 FROM entity_evidence ee
              WHERE ee.entity_id = e.id AND ee.evidence_role = 'supports'
          )
        ORDER BY entity_key
        """
    ).fetchall()
    problems.extend(
        f"canonical entity has no supporting evidence: {row['entity_key']}"
        for row in unsupported_entities
    )

    unsupported_relationships = connection.execute(
        """
        SELECT r.id
        FROM relationships r
        WHERE r.assertion_status = 'canonical'
          AND NOT EXISTS (
              SELECT 1 FROM relationship_evidence re
              WHERE re.relationship_id = r.id AND re.evidence_role = 'supports'
          )
        ORDER BY r.id
        """
    ).fetchall()
    problems.extend(
        f"canonical relationship has no supporting evidence: {row['id']}"
        for row in unsupported_relationships
    )

    return problems
