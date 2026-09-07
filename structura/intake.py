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
NORMALIZATION_COLUMNS = (
    "batch_key",
    "candidate_key",
    "normalized_manufacturer",
    "normalized_display_name",
    "entity_granularity",
    "parent_candidate_key",
    "normalized_category",
    "qualifying_event_type",
    "normalized_launch_date",
    "date_precision",
    "market_channel_notes",
    "decision_status",
    "rationale",
    "open_questions",
    "normalizer",
)
AUDIT_COLUMNS = (
    "batch_key",
    "finding_id",
    "finding_type",
    "severity",
    "affected_candidate_key",
    "proposed_candidate_key",
    "finding",
    "source_url",
    "source_locator",
    "source_evidence",
    "recommended_next_action",
    "disposition",
    "auditor",
)
NON_CANONICAL_STAGES = frozenset(
    {"planned", "scouting", "verification", "normalization", "audit", "human_review", "paused"}
)
KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,119}$")
FINDING_KEY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,119}$")
MAX_FIELD_LENGTH = 10_000
VERIFICATION_STATUSES = frozenset({"verified", "unsupported", "uncertain", "conflict", "not_assessed"})
CONFIDENCES = frozenset({"unknown", "low", "medium", "high"})
EVIDENCE_ROLES = frozenset({"supports", "contradicts", "context", "lead_only"})
ENTITY_GRANULARITIES = frozenset({"family", "model_variant", "sku_unresolved"})
DATE_PRECISIONS = frozenset({"exact", "month", "quarter", "year", "range", "unknown"})
NORMALIZATION_DECISIONS = frozenset({"proposed", "review_required", "blocked"})
AUDIT_FINDING_TYPES = frozenset(
    {"duplicate", "family_variant_overlap", "date_inheritance", "scope_error", "category_error", "omission_lead", "evidence_gap"}
)
AUDIT_SEVERITIES = frozenset({"info", "low", "medium", "high"})
AUDIT_DISPOSITIONS = frozenset({"open", "resolved_no_change", "follow_up"})


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


def _require_finding_key(value: str, row_number: str) -> None:
    if not FINDING_KEY_PATTERN.fullmatch(value):
        raise IntakeError(f"audit row {row_number} has an invalid finding_id: {value!r}")


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


def _validate_normalization(rows: list[dict[str, str]]) -> str:
    if not rows:
        raise IntakeError("normalization file has no records")
    batch_keys = {row["batch_key"] for row in rows}
    if len(batch_keys) != 1:
        raise IntakeError("normalization file must contain exactly one batch_key")
    batch_key = next(iter(batch_keys))
    _require_key(batch_key, "normalization", rows[0]["_row_number"])
    seen: set[str] = set()
    for row in rows:
        row_number = row["_row_number"]
        _require_key(row["candidate_key"], "normalization", row_number)
        if row["candidate_key"] in seen:
            raise IntakeError(f"duplicate candidate_key in normalization input: {row['candidate_key']}")
        seen.add(row["candidate_key"])
        if row["parent_candidate_key"]:
            _require_key(row["parent_candidate_key"], "normalization parent", row_number)
            if row["parent_candidate_key"] == row["candidate_key"]:
                raise IntakeError(f"normalization row {row_number} cannot be its own parent")
        for required in (
            "normalized_manufacturer",
            "normalized_display_name",
            "normalized_category",
            "qualifying_event_type",
            "rationale",
            "normalizer",
        ):
            if not row[required]:
                raise IntakeError(f"normalization row {row_number} requires {required}")
        if row["entity_granularity"] not in ENTITY_GRANULARITIES:
            raise IntakeError(f"normalization row {row_number} has invalid entity_granularity")
        if row["date_precision"] not in DATE_PRECISIONS:
            raise IntakeError(f"normalization row {row_number} has invalid date_precision")
        if row["decision_status"] not in NORMALIZATION_DECISIONS:
            raise IntakeError(f"normalization row {row_number} has invalid decision_status")
        if row["date_precision"] == "unknown" and row["normalized_launch_date"]:
            raise IntakeError(f"normalization row {row_number} cannot supply a date with unknown precision")
        if row["date_precision"] != "unknown" and not row["normalized_launch_date"]:
            raise IntakeError(f"normalization row {row_number} requires normalized_launch_date")
    return batch_key


def import_normalization(db_path: Path | str, normalization_path: Path | str) -> ImportResult:
    """Import normalization proposals while leaving entity fields unchanged."""
    normalization_file = Path(normalization_path).resolve()
    rows = _read_csv(normalization_file, NORMALIZATION_COLUMNS, "normalization")
    batch_key = _validate_normalization(rows)
    digest = _digest((normalization_file,), "normalization")
    run_key = f"{batch_key}-{digest[:12]}"
    with connect(db_path) as connection:
        batch_id, candidates, previous_run_key = _verification_context(connection, batch_key, rows, digest)
        if previous_run_key is not None:
            return ImportResult(previous_run_key, True, len(rows), 0)
        parent_keys = {row["parent_candidate_key"] for row in rows if row["parent_candidate_key"]}
        unknown_parents = sorted(parent_keys - set(candidates))
        if unknown_parents:
            raise IntakeError("normalization references parent candidate keys not staged for this batch: " + ", ".join(unknown_parents))
        existing = connection.execute(
            "SELECT c.candidate_key FROM normalization_proposals n JOIN intake_candidate_records c ON c.id=n.intake_candidate_record_id JOIN research_import_runs r ON r.id=n.import_run_id WHERE r.research_batch_id=? AND c.candidate_key IN ({})".format(
                ",".join("?" for _ in rows)
            ),
            [batch_id, *[row["candidate_key"] for row in rows]],
        ).fetchall()
        if existing:
            raise IntakeError(
                "normalization proposals already exist and require a human merge decision: "
                + ", ".join(sorted(row["candidate_key"] for row in existing))
            )
        connection.execute(
            "INSERT INTO research_import_runs(run_key, research_batch_id, pipeline_stage, input_digest, candidate_path, source_path, candidate_count, source_count, importer) VALUES (?, ?, 'normalization', ?, ?, NULL, ?, 0, ?)",
            (run_key, batch_id, digest, str(normalization_file), len(rows), "structura-normalization-v1"),
        )
        run_id = int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])
        for row in rows:
            connection.execute(
                "INSERT INTO normalization_proposals(import_run_id, intake_candidate_record_id, normalized_manufacturer, normalized_display_name, entity_granularity, parent_intake_candidate_record_id, normalized_category, qualifying_event_type, normalized_launch_date, date_precision, market_channel_notes, decision_status, rationale, open_questions, normalizer) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    run_id,
                    candidates[row["candidate_key"]],
                    row["normalized_manufacturer"],
                    row["normalized_display_name"],
                    row["entity_granularity"],
                    candidates.get(row["parent_candidate_key"]),
                    row["normalized_category"],
                    row["qualifying_event_type"],
                    row["normalized_launch_date"] or None,
                    row["date_precision"],
                    row["market_channel_notes"] or None,
                    row["decision_status"],
                    row["rationale"],
                    row["open_questions"] or None,
                    row["normalizer"],
                ),
            )
        connection.execute("UPDATE research_batches SET workflow_status='normalization', updated_at=CURRENT_TIMESTAMP WHERE id=?", (batch_id,))
    return ImportResult(run_key, False, len(rows), 0)


def _validate_audit(rows: list[dict[str, str]]) -> str:
    if not rows:
        raise IntakeError("audit file has no findings")
    batch_keys = {row["batch_key"] for row in rows}
    if len(batch_keys) != 1:
        raise IntakeError("audit file must contain exactly one batch_key")
    batch_key = next(iter(batch_keys))
    _require_key(batch_key, "audit", rows[0]["_row_number"])
    seen: set[str] = set()
    for row in rows:
        row_number = row["_row_number"]
        _require_finding_key(row["finding_id"], row_number)
        if row["finding_id"] in seen:
            raise IntakeError(f"duplicate finding_id in audit input: {row['finding_id']}")
        seen.add(row["finding_id"])
        for candidate_key in _split_key_list(row["affected_candidate_key"]):
            _require_key(candidate_key, "audit affected candidate", row_number)
        for proposed_key in _split_key_list(row["proposed_candidate_key"]):
            _require_key(proposed_key, "audit proposed candidate", row_number)
        if row["finding_type"] not in AUDIT_FINDING_TYPES:
            raise IntakeError(f"audit row {row_number} has invalid finding_type")
        if row["severity"] not in AUDIT_SEVERITIES:
            raise IntakeError(f"audit row {row_number} has invalid severity")
        if row["disposition"] not in AUDIT_DISPOSITIONS:
            raise IntakeError(f"audit row {row_number} has invalid disposition")
        for required in ("finding", "recommended_next_action", "auditor"):
            if not row[required]:
                raise IntakeError(f"audit row {row_number} requires {required}")
        if row["source_url"] and not _is_http_url(row["source_url"]):
            raise IntakeError(f"audit row {row_number} has a non-http source URL")
        if row["source_evidence"] and not row["source_url"]:
            raise IntakeError(f"audit row {row_number} cannot supply source evidence without a source URL")
    return batch_key


def _split_key_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def import_audit(db_path: Path | str, audit_path: Path | str) -> ImportResult:
    """Import immutable audit findings and omission leads without adding entities."""
    audit_file = Path(audit_path).resolve()
    rows = _read_csv(audit_file, AUDIT_COLUMNS, "audit")
    batch_key = _validate_audit(rows)
    digest = _digest((audit_file,), "audit")
    run_key = f"{batch_key}-{digest[:12]}"
    with connect(db_path) as connection:
        batch = connection.execute("SELECT id FROM research_batches WHERE batch_key=?", (batch_key,)).fetchone()
        if batch is None:
            raise IntakeError(f"audit batch is not staged: {batch_key}")
        batch_id = int(batch["id"])
        previous = connection.execute(
            "SELECT run_key FROM research_import_runs WHERE research_batch_id=? AND input_digest=?",
            (batch_id, digest),
        ).fetchone()
        if previous is not None:
            return ImportResult(previous["run_key"], True, len(rows), len({row["source_url"] for row in rows if row["source_url"]}))
        candidates = {
            row["candidate_key"]: int(row["id"])
            for row in connection.execute(
                "SELECT c.id, c.candidate_key FROM intake_candidate_records c JOIN research_import_runs r ON r.id=c.import_run_id WHERE r.research_batch_id=?",
                (batch_id,),
            ).fetchall()
        }
        affected_keys = {
            candidate_key
            for row in rows
            for candidate_key in _split_key_list(row["affected_candidate_key"])
        }
        unknown = sorted(affected_keys - set(candidates))
        if unknown:
            raise IntakeError("audit references candidate keys not staged for this batch: " + ", ".join(unknown))
        existing_ids = connection.execute(
            "SELECT a.finding_key FROM audit_findings a JOIN research_import_runs r ON r.id=a.import_run_id WHERE r.research_batch_id=? AND a.finding_key IN ({})".format(
                ",".join("?" for _ in rows)
            ),
            [batch_id, *[row["finding_id"] for row in rows]],
        ).fetchall()
        if existing_ids:
            raise IntakeError(
                "audit finding IDs already exist and require a human merge decision: "
                + ", ".join(sorted(row["finding_key"] for row in existing_ids))
            )
        source_count = len({row["source_url"] for row in rows if row["source_url"]})
        connection.execute(
            "INSERT INTO research_import_runs(run_key, research_batch_id, pipeline_stage, input_digest, candidate_path, source_path, candidate_count, source_count, importer) VALUES (?, ?, 'audit', ?, ?, NULL, ?, ?, ?)",
            (run_key, batch_id, digest, str(audit_file), len(rows), source_count, "structura-audit-v1"),
        )
        run_id = int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])
        for row in rows:
            connection.execute(
                "INSERT INTO audit_findings(import_run_id, finding_key, finding_type, severity, finding, source_url, source_locator, source_evidence, recommended_next_action, disposition, auditor) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    run_id,
                    row["finding_id"],
                    row["finding_type"],
                    row["severity"],
                    row["finding"],
                    row["source_url"] or None,
                    row["source_locator"] or None,
                    row["source_evidence"] or None,
                    row["recommended_next_action"],
                    row["disposition"],
                    row["auditor"],
                ),
            )
            finding_id = int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])
            for candidate_key in _split_key_list(row["affected_candidate_key"]):
                connection.execute(
                    "INSERT INTO audit_finding_candidate_refs(audit_finding_id, intake_candidate_record_id) VALUES (?, ?)",
                    (finding_id, candidates[candidate_key]),
                )
            for proposed_key in _split_key_list(row["proposed_candidate_key"]):
                connection.execute(
                    "INSERT INTO audit_finding_proposed_keys(audit_finding_id, proposed_candidate_key) VALUES (?, ?)",
                    (finding_id, proposed_key),
                )
        connection.execute("UPDATE research_batches SET workflow_status='audit', updated_at=CURRENT_TIMESTAMP WHERE id=?", (batch_id,))
    return ImportResult(run_key, False, len(rows), source_count)
