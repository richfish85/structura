from __future__ import annotations

import csv
import hashlib
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

from .db import connect


CANDIDATE_COLUMNS = (
    "batch_key",
    "candidate_key",
    "manufacturer_raw",
    "product_name_raw",
    "model_number_raw",
    "product_type_raw",
    "announced_date_raw",
    "release_date_raw",
    "market_scope_raw",
    "source_1_url",
    "source_2_url",
    "notes",
)
SOURCE_COLUMNS = (
    "source_key",
    "title",
    "publisher",
    "source_type",
    "source_tier",
    "url",
    "publication_date",
    "accessed_date",
    "scope_note",
)
VERIFICATION_COLUMNS = (
    "batch_key",
    "candidate_key",
    "identity_status",
    "manufacturer_status",
    "category_status",
    "release_timing_status",
    "confidence",
    "source_key",
    "source_tier",
    "evidence_role",
    "locator",
    "evidence_note",
    "conflict_note",
    "verifier",
)
VERIFICATION_REPORT_COLUMNS = (
    "batch_key",
    "candidate_key",
    "identity_status",
    "manufacturer_status",
    "category_status",
    "timing_status",
    "inclusion_recommendation",
    "verified_event_type",
    "verified_timing_raw",
    "date_precision",
    "source_1_url",
    "source_1_locator",
    "source_1_evidence",
    "source_2_url",
    "source_2_locator",
    "source_2_evidence",
    "contradictions_or_limits",
    "unresolved_questions",
    "verifier_notes",
)
NON_CANONICAL_STAGES = frozenset(
    {"planned", "scouting", "verification", "normalization", "audit", "human_review", "paused"}
)
KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,119}$")
MAX_FIELD_LENGTH = 10_000
VERIFICATION_STATUSES = frozenset({"verified", "unsupported", "uncertain", "conflict", "not_assessed"})
CONFIDENCES = frozenset({"unknown", "low", "medium", "high"})
EVIDENCE_ROLES = frozenset({"supports", "contradicts", "context", "lead_only"})


class IntakeError(ValueError):
    """A hand-off cannot safely be added to the review database."""


@dataclass(frozen=True)
class ImportResult:
    run_key: str
    already_imported: bool
    candidate_count: int
    source_count: int


def _read_csv(path: Path, columns: tuple[str, ...], label: str) -> list[dict[str, str]]:
    if not path.is_file():
        raise IntakeError(f"{label} file not found: {path}")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, skipinitialspace=True)
            actual = tuple(reader.fieldnames or ())
            if actual != columns:
                raise IntakeError(
                    f"{label} columns must be exactly: {', '.join(columns)}"
                )
            rows = []
            for row_number, row in enumerate(reader, start=2):
                cleaned = {column: (row.get(column) or "").strip() for column in columns}
                if any("\x00" in value or len(value) > MAX_FIELD_LENGTH for value in cleaned.values()):
                    raise IntakeError(f"{label} row {row_number} contains an unsafe or oversized field")
                if not any(cleaned.values()):
                    continue
                cleaned["_row_number"] = str(row_number)
                rows.append(cleaned)
            return rows
    except UnicodeDecodeError as error:
        raise IntakeError(f"{label} must be UTF-8 text: {path}") from error
    except csv.Error as error:
        raise IntakeError(f"{label} is not valid CSV: {path}") from error


def _is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _require_key(value: str, label: str, row_number: str) -> None:
    if not KEY_PATTERN.fullmatch(value):
        raise IntakeError(f"{label} row {row_number} has an invalid key: {value!r}")


def _validate_candidates(rows: list[dict[str, str]]) -> str:
    if not rows:
        raise IntakeError("candidate file has no records")
    batch_keys = {row["batch_key"] for row in rows}
    if len(batch_keys) != 1:
        raise IntakeError("candidate file must contain exactly one batch_key")
    batch_key = next(iter(batch_keys))
    _require_key(batch_key, "candidate", rows[0]["_row_number"])
    seen: set[str] = set()
    for row in rows:
        row_number = row["_row_number"]
        _require_key(row["candidate_key"], "candidate", row_number)
        if row["candidate_key"] in seen:
            raise IntakeError(f"duplicate candidate_key in input: {row['candidate_key']}")
        seen.add(row["candidate_key"])
        for required in ("manufacturer_raw", "product_name_raw", "product_type_raw", "source_1_url", "notes"):
            if not row[required]:
                raise IntakeError(f"candidate row {row_number} requires {required}")
        for url_column in ("source_1_url", "source_2_url"):
            if row[url_column] and not _is_http_url(row[url_column]):
                raise IntakeError(f"candidate row {row_number} has a non-http source URL")
    return batch_key


def _validate_sources(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    by_url: dict[str, dict[str, str]] = {}
    seen_keys: set[str] = set()
    for row in rows:
        row_number = row["_row_number"]
        _require_key(row["source_key"], "source", row_number)
        if row["source_key"] in seen_keys:
            raise IntakeError(f"duplicate source_key in input: {row['source_key']}")
        seen_keys.add(row["source_key"])
        for required in ("title", "source_type", "source_tier", "url", "accessed_date", "scope_note"):
            if not row[required]:
                raise IntakeError(f"source row {row_number} requires {required}")
        try:
            tier = int(row["source_tier"])
        except ValueError as error:
            raise IntakeError(f"source row {row_number} has an invalid source_tier") from error
        if tier not in {1, 2, 3, 4}:
            raise IntakeError(f"source row {row_number} has source_tier outside 1 through 4")
        if not _is_http_url(row["url"]):
            raise IntakeError(f"source row {row_number} has a non-http URL")
        if row["url"] in by_url:
            raise IntakeError(f"duplicate source URL in input: {row['url']}")
        by_url[row["url"]] = row
    return by_url


def _digest(files: Iterable[Path], stage: str) -> str:
    hasher = hashlib.sha256()
    hasher.update(f"structura-intake-v1\x00{stage}\x00".encode())
    for path in files:
        hasher.update(path.read_bytes())
        hasher.update(b"\x00")
    return hasher.hexdigest()


def _source_values_match(existing: sqlite3.Row, proposed: dict[str, str]) -> bool:
    return (
        existing["title"] == proposed["title"]
        and (existing["publisher"] or "") == proposed["publisher"]
        and existing["source_type"] == proposed["source_type"]
        and existing["source_tier"] == int(proposed["source_tier"])
        and (existing["url"] or "") == proposed["url"]
        and (existing["publication_date"] or "") == proposed["publication_date"]
        and existing["accessed_date"] == proposed["accessed_date"]
        and (existing["notes"] or "") == proposed["scope_note"]
    )


def import_batch(
    db_path: Path | str,
    candidate_path: Path | str,
    source_path: Path | str,
    *,
    stage: str = "scouting",
) -> ImportResult:
    """Load one agent hand-off as non-canonical review data.

    Every validation occurs before data are written. Identical inputs for one
    batch are recognised by digest and do not create a second run.
    """
    if stage not in NON_CANONICAL_STAGES:
        raise IntakeError("only a non-canonical workflow stage may be imported")
    candidates_file = Path(candidate_path).resolve()
    sources_file = Path(source_path).resolve()
    candidates = _read_csv(candidates_file, CANDIDATE_COLUMNS, "candidate")
    sources = _read_csv(sources_file, SOURCE_COLUMNS, "source")
    batch_key = _validate_candidates(candidates)
    sources_by_url = _validate_sources(sources)
    for row in candidates:
        for url_column in ("source_1_url", "source_2_url"):
            if row[url_column] and row[url_column] not in sources_by_url:
                raise IntakeError(
                    f"candidate row {row['_row_number']} references a source URL absent from source file"
                )
    digest = _digest((candidates_file, sources_file), stage)
    run_key = f"{batch_key}-{digest[:12]}"

    with connect(db_path) as connection:
        batch = connection.execute(
            "SELECT id FROM research_batches WHERE batch_key=?", (batch_key,)
        ).fetchone()
        if batch is None:
            connection.execute(
                "INSERT INTO research_batches(batch_key, title, scope_note, workflow_status) VALUES (?, ?, ?, ?)",
                (batch_key, f"Imported research batch: {batch_key}", "Scope supplied by an external research hand-off; review required.", stage),
            )
            batch_id = int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])
        else:
            batch_id = int(batch["id"])

        previous = connection.execute(
            "SELECT run_key, candidate_count, source_count FROM research_import_runs WHERE research_batch_id=? AND input_digest=?",
            (batch_id, digest),
        ).fetchone()
        if previous is not None:
            return ImportResult(previous["run_key"], True, previous["candidate_count"], previous["source_count"])

        existing_keys = {
            row["entity_key"]
            for row in connection.execute(
                "SELECT entity_key FROM entities WHERE entity_key IN ({})".format(
                    ",".join("?" for _ in candidates)
                ),
                [row["candidate_key"] for row in candidates],
            ).fetchall()
        }
        if existing_keys:
            raise IntakeError(
                "candidate keys already exist and require a human merge decision: "
                + ", ".join(sorted(existing_keys))
            )

        source_ids: dict[str, int] = {}
        for source in sources:
            existing = connection.execute("SELECT * FROM sources WHERE source_key=?", (source["source_key"],)).fetchone()
            if existing is not None:
                if not _source_values_match(existing, source):
                    raise IntakeError(f"source_key conflicts with existing source: {source['source_key']}")
                source_ids[source["url"]] = int(existing["id"])
                continue
            connection.execute(
                "INSERT INTO sources(source_key, title, publisher, source_type, source_tier, url, publication_date, accessed_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (source["source_key"], source["title"], source["publisher"] or None, source["source_type"], int(source["source_tier"]), source["url"], source["publication_date"] or None, source["accessed_date"], source["scope_note"]),
            )
            source_ids[source["url"]] = int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])

        connection.execute(
            "INSERT INTO research_import_runs(run_key, research_batch_id, pipeline_stage, input_digest, candidate_path, source_path, candidate_count, source_count, importer) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (run_key, batch_id, stage, digest, str(candidates_file), str(sources_file), len(candidates), len(sources), "structura-intake-v1"),
        )
        run_id = int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])
        for source_id in sorted(set(source_ids.values())):
            connection.execute(
                "INSERT INTO research_import_run_sources(import_run_id, source_id) VALUES (?, ?)",
                (run_id, source_id),
            )
        for row in candidates:
            connection.execute(
                "INSERT INTO entities(entity_key, name, entity_type_code, description, record_status, confidence, research_batch_id) VALUES (?, ?, 'product', ?, 'candidate', 'unknown', ?)",
                (row["candidate_key"], row["product_name_raw"], row["notes"], batch_id),
            )
            entity_id = int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])
            connection.execute(
                "INSERT INTO product_details(entity_id, model_number, announced_date, release_date, date_precision, market_scope, notes) VALUES (?, ?, ?, ?, 'unknown', ?, ?)",
                (entity_id, row["model_number_raw"] or None, row["announced_date_raw"] or None, row["release_date_raw"] or None, row["market_scope_raw"] or None, "Imported raw fields; no normalization or date inference has been applied."),
            )
            connection.execute(
                "INSERT INTO intake_candidate_records(import_run_id, entity_id, source_row_number, candidate_key, manufacturer_raw, product_name_raw, model_number_raw, product_type_raw, announced_date_raw, release_date_raw, market_scope_raw, source_1_url, source_2_url, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (run_id, entity_id, int(row["_row_number"]), row["candidate_key"], row["manufacturer_raw"], row["product_name_raw"], row["model_number_raw"] or None, row["product_type_raw"], row["announced_date_raw"] or None, row["release_date_raw"] or None, row["market_scope_raw"] or None, row["source_1_url"], row["source_2_url"] or None, row["notes"]),
            )
            for source_url in dict.fromkeys(url for url in (row["source_1_url"], row["source_2_url"]) if url):
                connection.execute(
                    "INSERT INTO entity_evidence(entity_id, source_id, field_name, evidence_role, locator, evidence_note) VALUES (?, ?, 'imported_source_url', 'lead_only', NULL, ?)",
                    (entity_id, source_ids[source_url], "Imported source reference; independent verification has not occurred."),
                )
        connection.execute(
            "UPDATE research_batches SET workflow_status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (stage, batch_id),
        )
    return ImportResult(run_key, False, len(candidates), len(sources))


def _validate_verification(rows: list[dict[str, str]]) -> str:
    if not rows:
        raise IntakeError("verification file has no records")
    batch_keys = {row["batch_key"] for row in rows}
    if len(batch_keys) != 1:
        raise IntakeError("verification file must contain exactly one batch_key")
    batch_key = next(iter(batch_keys))
    _require_key(batch_key, "verification", rows[0]["_row_number"])
    candidate_keys: set[str] = set()
    for row in rows:
        row_number = row["_row_number"]
        _require_key(row["candidate_key"], "verification", row_number)
        if row["candidate_key"] in candidate_keys:
            raise IntakeError(f"duplicate candidate_key in verification input: {row['candidate_key']}")
        candidate_keys.add(row["candidate_key"])
        for field in ("identity_status", "manufacturer_status", "category_status", "release_timing_status"):
            if row[field] not in VERIFICATION_STATUSES:
                raise IntakeError(f"verification row {row_number} has an invalid {field}")
        if row["confidence"] not in CONFIDENCES:
            raise IntakeError(f"verification row {row_number} has invalid confidence")
        if row["evidence_role"] not in EVIDENCE_ROLES:
            raise IntakeError(f"verification row {row_number} has invalid evidence_role")
        for required in ("source_key", "source_tier", "evidence_note", "verifier"):
            if not row[required]:
                raise IntakeError(f"verification row {row_number} requires {required}")
        _require_key(row["source_key"], "verification", row_number)
        try:
            tier = int(row["source_tier"])
        except ValueError as error:
            raise IntakeError(f"verification row {row_number} has an invalid source_tier") from error
        if tier not in {1, 2, 3, 4}:
            raise IntakeError(f"verification row {row_number} has source_tier outside 1 through 4")
    return batch_key


def _verification_file_columns(path: Path) -> tuple[str, ...]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return tuple(next(csv.reader(handle, skipinitialspace=True), []))
    except UnicodeDecodeError as error:
        raise IntakeError(f"verification must be UTF-8 text: {path}") from error
    except csv.Error as error:
        raise IntakeError(f"verification is not valid CSV: {path}") from error


def _verification_context(connection: sqlite3.Connection, batch_key: str, rows: list[dict[str, str]], digest: str) -> tuple[int, dict[str, int], str | None]:
    batch = connection.execute("SELECT id FROM research_batches WHERE batch_key=?", (batch_key,)).fetchone()
    if batch is None:
        raise IntakeError(f"verification batch is not staged: {batch_key}")
    batch_id = int(batch["id"])
    previous = connection.execute("SELECT run_key FROM research_import_runs WHERE research_batch_id=? AND input_digest=?", (batch_id, digest)).fetchone()
    candidates = {row["candidate_key"]: int(row["id"]) for row in connection.execute("SELECT c.id, c.candidate_key FROM intake_candidate_records c JOIN research_import_runs r ON r.id=c.import_run_id WHERE r.research_batch_id=?", (batch_id,)).fetchall()}
    unknown_keys = sorted({row["candidate_key"] for row in rows} - set(candidates))
    if unknown_keys:
        raise IntakeError("verification references candidate keys not staged for this batch: " + ", ".join(unknown_keys))
    return batch_id, candidates, previous["run_key"] if previous is not None else None


def _import_verification_assertions(
    db_path: Path | str, verification_path: Path | str
) -> ImportResult:
    """Add independently produced verification assertions without promotion."""
    verification_file = Path(verification_path).resolve()
    rows = _read_csv(verification_file, VERIFICATION_COLUMNS, "verification")
    batch_key = _validate_verification(rows)
    digest = _digest((verification_file,), "verification")
    run_key = f"{batch_key}-{digest[:12]}"
    with connect(db_path) as connection:
        batch_id, candidates, previous_run_key = _verification_context(connection, batch_key, rows, digest)
        if previous_run_key is not None:
            return ImportResult(previous_run_key, True, len(rows), len({row['source_key'] for row in rows}))
        sources = {
            row["source_key"]: row
            for row in connection.execute(
                "SELECT id, source_key, source_tier FROM sources WHERE source_key IN ({})".format(
                    ",".join("?" for _ in rows)
                ),
                [row["source_key"] for row in rows],
            ).fetchall()
        }
        unknown_sources = sorted({row["source_key"] for row in rows} - set(sources))
        if unknown_sources:
            raise IntakeError("verification references source keys not registered in SQLite: " + ", ".join(unknown_sources))
        for row in rows:
            if int(sources[row["source_key"]]["source_tier"]) != int(row["source_tier"]):
                raise IntakeError(f"verification source_tier disagrees with registered source: {row['source_key']}")
        source_ids = sorted({int(sources[row["source_key"]]["id"]) for row in rows})
        connection.execute(
            "INSERT INTO research_import_runs(run_key, research_batch_id, pipeline_stage, input_digest, candidate_path, source_path, candidate_count, source_count, importer) VALUES (?, ?, 'verification', ?, ?, NULL, ?, ?, ?)",
            (run_key, batch_id, digest, str(verification_file), len(rows), len(source_ids), "structura-verification-v1"),
        )
        run_id = int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])
        for source_id in source_ids:
            connection.execute("INSERT INTO research_import_run_sources(import_run_id, source_id) VALUES (?, ?)", (run_id, source_id))
        for row in rows:
            connection.execute(
                "INSERT INTO verification_records(import_run_id, intake_candidate_record_id, identity_status, manufacturer_status, category_status, release_timing_status, confidence, source_id, source_tier, evidence_role, locator, evidence_note, conflict_note, verifier) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (run_id, candidates[row["candidate_key"]], row["identity_status"], row["manufacturer_status"], row["category_status"], row["release_timing_status"], row["confidence"], sources[row["source_key"]]["id"], int(row["source_tier"]), row["evidence_role"], row["locator"] or None, row["evidence_note"], row["conflict_note"] or None, row["verifier"]),
            )
        connection.execute("UPDATE research_batches SET workflow_status='verification', updated_at=CURRENT_TIMESTAMP WHERE id=?", (batch_id,))
    return ImportResult(run_key, False, len(rows), len(source_ids))


def _validate_verification_report(rows: list[dict[str, str]]) -> str:
    if not rows:
        raise IntakeError("verification report has no records")
    batch_keys = {row["batch_key"] for row in rows}
    if len(batch_keys) != 1:
        raise IntakeError("verification report must contain exactly one batch_key")
    batch_key = next(iter(batch_keys))
    _require_key(batch_key, "verification report", rows[0]["_row_number"])
    seen: set[str] = set()
    for row in rows:
        row_number = row["_row_number"]
        _require_key(row["candidate_key"], "verification report", row_number)
        if row["candidate_key"] in seen:
            raise IntakeError(f"duplicate candidate_key in verification report: {row['candidate_key']}")
        seen.add(row["candidate_key"])
        for required in ("identity_status", "manufacturer_status", "category_status", "timing_status", "inclusion_recommendation", "verified_event_type", "verified_timing_raw", "date_precision", "source_1_url", "source_1_evidence"):
            if not row[required]:
                raise IntakeError(f"verification report row {row_number} requires {required}")
        for url_field in ("source_1_url", "source_2_url"):
            if row[url_field] and not _is_http_url(row[url_field]):
                raise IntakeError(f"verification report row {row_number} has a non-http source URL")
        if bool(row["source_2_url"]) != bool(row["source_2_evidence"]):
            raise IntakeError(f"verification report row {row_number} requires source_2_url and source_2_evidence together")
    return batch_key


def _import_verification_report(db_path: Path | str, verification_path: Path | str) -> ImportResult:
    verification_file = Path(verification_path).resolve()
    rows = _read_csv(verification_file, VERIFICATION_REPORT_COLUMNS, "verification report")
    batch_key = _validate_verification_report(rows)
    digest = _digest((verification_file,), "verification")
    run_key = f"{batch_key}-{digest[:12]}"
    with connect(db_path) as connection:
        batch_id, candidates, previous_run_key = _verification_context(connection, batch_key, rows, digest)
        source_urls = {url for row in rows for url in (row["source_1_url"], row["source_2_url"]) if url}
        sources_by_url = {row["url"]: row for row in connection.execute("SELECT id, url FROM sources WHERE url IN ({})".format(",".join("?" for _ in source_urls)), sorted(source_urls)).fetchall()}
        missing_urls = sorted(source_urls - set(sources_by_url))
        if missing_urls:
            raise IntakeError("verification report references source URLs not registered in SQLite: " + ", ".join(missing_urls))
        if previous_run_key is not None:
            return ImportResult(previous_run_key, True, len(rows), len(source_urls))
        connection.execute("INSERT INTO research_import_runs(run_key, research_batch_id, pipeline_stage, input_digest, candidate_path, source_path, candidate_count, source_count, importer) VALUES (?, ?, 'verification', ?, ?, NULL, ?, ?, ?)", (run_key, batch_id, digest, str(verification_file), len(rows), len(source_urls), "structura-verification-report-v1"))
        run_id = int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])
        for source in sorted(sources_by_url.values(), key=lambda row: row["id"]):
            connection.execute("INSERT INTO research_import_run_sources(import_run_id, source_id) VALUES (?, ?)", (run_id, source["id"]))
        for row in rows:
            source_1_id = int(sources_by_url[row["source_1_url"]]["id"])
            connection.execute("INSERT INTO verification_records(import_run_id, intake_candidate_record_id, identity_status, manufacturer_status, category_status, release_timing_status, confidence, source_id, source_tier, evidence_role, locator, evidence_note, conflict_note, verifier) VALUES (?, ?, ?, ?, ?, ?, 'unknown', ?, (SELECT source_tier FROM sources WHERE id=?), 'supports', ?, ?, ?, ?)", (run_id, candidates[row["candidate_key"]], row["identity_status"], row["manufacturer_status"], row["category_status"], row["timing_status"], source_1_id, source_1_id, row["source_1_locator"] or None, row["source_1_evidence"], row["contradictions_or_limits"] or None, "unspecified in report; see verifier_notes"))
            verification_id = int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])
            connection.execute("INSERT INTO verification_report_records(verification_record_id, inclusion_recommendation, verified_event_type, verified_timing_raw, date_precision_raw, source_1_url, source_1_locator, source_1_evidence, source_2_url, source_2_locator, source_2_evidence, contradictions_or_limits, unresolved_questions, verifier_notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (verification_id, row["inclusion_recommendation"], row["verified_event_type"], row["verified_timing_raw"], row["date_precision"], row["source_1_url"], row["source_1_locator"] or None, row["source_1_evidence"], row["source_2_url"] or None, row["source_2_locator"] or None, row["source_2_evidence"] or None, row["contradictions_or_limits"] or None, row["unresolved_questions"] or None, row["verifier_notes"]))
            connection.execute("INSERT INTO verification_evidence_references(verification_record_id, source_id, source_position, locator, evidence_note) VALUES (?, ?, 1, ?, ?)", (verification_id, source_1_id, row["source_1_locator"] or None, row["source_1_evidence"]))
            if row["source_2_url"]:
                connection.execute("INSERT INTO verification_evidence_references(verification_record_id, source_id, source_position, locator, evidence_note) VALUES (?, ?, 2, ?, ?)", (verification_id, int(sources_by_url[row["source_2_url"]]["id"]), row["source_2_locator"] or None, row["source_2_evidence"]))
        connection.execute("UPDATE research_batches SET workflow_status='verification', updated_at=CURRENT_TIMESTAMP WHERE id=?", (batch_id,))
    return ImportResult(run_key, False, len(rows), len(source_urls))


def import_verification(db_path: Path | str, verification_path: Path | str) -> ImportResult:
    """Import either supported verification hand-off shape without promotion."""
    path = Path(verification_path).resolve()
    columns = _verification_file_columns(path)
    if columns == VERIFICATION_COLUMNS:
        return _import_verification_assertions(db_path, path)
    if columns == VERIFICATION_REPORT_COLUMNS:
        return _import_verification_report(db_path, path)
    raise IntakeError(
        "verification columns must exactly match the assertion template or the verification report template"
    )
