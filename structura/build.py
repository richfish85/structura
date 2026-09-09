"""Reproducible local snapshots; a pointer changes only after every gate passes."""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from pathlib import Path

from .db import PROJECT_ROOT, connect, initialize, validate
from .intake import (IntakeError, import_batch, import_verification, import_normalization,
                     import_audit, import_context, import_review_decisions)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_path(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"Input must be a file inside the project: {value}")
    return path


def validate_manifest(root: Path, manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("version") != 1 or not manifest.get("steps"):
        raise ValueError("Unsupported or empty build manifest")
    for step in manifest["steps"]:
        for item in step["files"].values():
            path = checked_path(root, item["path"])
            if digest(path) != item["sha256"]:
                raise ValueError(f"Input hash mismatch: {item['path']}")
    if manifest.get("connected"):
        for item in manifest["connected"].values():
            path = checked_path(root, item["path"])
            if digest(path) != item["sha256"]:
                raise ValueError(f"Connected input hash mismatch: {item['path']}")
    return manifest


def import_steps(root: Path, db: Path, manifest: dict) -> None:
    contracts = {
        "batch": (import_batch, ("candidates", "sources")),
        "verification": (import_verification, ("verification",)),
        "normalization": (import_normalization, ("normalization",)),
        "audit": (import_audit, ("audit",)),
        "context": (import_context, ("intent", "benchmarks", "sources")),
        "review-decisions": (import_review_decisions, ("decisions",)),
    }
    for step in manifest["steps"]:
        if step["stage"] not in contracts:
            raise ValueError(f"Unknown stage: {step['stage']}")
        function, keys = contracts[step["stage"]]
        if set(step["files"]) != set(keys):
            raise ValueError(f"Wrong input files for {step['stage']}")
        try:
            function(db, *(checked_path(root, step["files"][key]["path"]) for key in keys))
        except (ValueError, IntakeError) as error:
            raise ValueError(f"{step['stage']} failed: {error}") from error


def summary(db: Path) -> dict:
    with connect(db, read_only=True) as c:
        cohorts = [dict(r) for r in c.execute("""
            SELECT b.batch_key, COUNT(DISTINCT i.id) AS candidates,
              COUNT(DISTINCT v.intake_candidate_record_id) AS verification_records,
              COUNT(DISTINCT n.intake_candidate_record_id) AS normalization_records
            FROM research_batches b JOIN research_import_runs r ON r.research_batch_id=b.id
            JOIN intake_candidate_records i ON i.import_run_id=r.id
            LEFT JOIN verification_records v ON v.intake_candidate_record_id=i.id
            LEFT JOIN normalization_proposals n ON n.intake_candidate_record_id=i.id
            GROUP BY b.id ORDER BY b.batch_key
        """)]
        result = {"cohorts": cohorts}
        for table in ("entities", "relationships", "sources", "audit_findings", "product_intent_claims", "benchmark_observations"):
            result[table] = c.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        result["historical_candidates"] = c.execute("SELECT count(*) FROM intake_candidate_records").fetchone()[0]
        result["canonical_entities"] = c.execute("SELECT count(*) FROM entities WHERE record_status='canonical'").fetchone()[0]
        result["reviewed_candidates"] = c.execute("SELECT count(DISTINCT intake_candidate_record_id) FROM candidate_discrepancy_reviews").fetchone()[0]
        result["open_audit_findings"] = c.execute("SELECT count(*) FROM audit_findings WHERE disposition<>'resolved_no_change'").fetchone()[0]
        result["usability_trial"] = "pending_real_participants"
        return result


def build(root: Path = PROJECT_ROOT, manifest_path: Path | None = None) -> dict:
    root = root.resolve()
    manifest_path = manifest_path or root / "data/build-manifest.json"
    manifest = validate_manifest(root, manifest_path)
    # Preserve every previous successful snapshot. Neither raw packets nor an old
    # database are edited by a rebuild. Failed snapshots cannot become current.
    identity = hashlib.sha256(manifest_path.read_bytes())
    for path in sorted([*(root / "schema").glob("*.sql"), *(root / "structura").rglob("*.py"), *(root / "structura/assets").glob("*")]):
        identity.update(path.relative_to(root).as_posix().encode())
        identity.update(path.read_bytes())
    build_id = identity.hexdigest()[:16] + "-" + uuid.uuid4().hex[:8]
    snapshot = root / "data/builds" / build_id
    snapshot.mkdir(parents=True, exist_ok=False)
    db = snapshot / "structura.db"
    try:
        initialize(db)
        import_steps(root, db, manifest)
        if manifest.get("connected"):
            from .connected import import_connected
            import_connected(db, checked_path(root, manifest["connected"]["packet"]["path"]),
                             checked_path(root, manifest["connected"]["verification"]["path"]),root)
        with connect(db, read_only=True) as c:
            problems = validate(c)
            if c.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                problems.append("SQLite integrity check failed")
            if problems:
                raise ValueError("; ".join(problems))
        status = summary(db)
        from .explorer import render_explorer, validate_site
        render_explorer(db, snapshot / "site", status)
        site_problems=validate_site(snapshot / "site")
        if site_problems:
            raise ValueError('Explorer link validation failed: '+ '; '.join(site_problems[:10]))
        # A content manifest permits later corruption checks without treating
        # equal input hashes as proof of factual truth.
        files = {p.relative_to(snapshot).as_posix(): digest(p) for p in sorted(snapshot.rglob("*")) if p.is_file()}
        (snapshot / "files.json").write_text(json.dumps(files, indent=2)+"\n", encoding="utf-8")
        (snapshot / "status.json").write_text(json.dumps(status, indent=2)+"\n", encoding="utf-8")
        pointer = {"version": 1, "build_id": build_id, "snapshot": snapshot.relative_to(root).as_posix(), "status": status}
        temporary = root / "data" / (".current-" + uuid.uuid4().hex + ".json")
        temporary.write_text(json.dumps(pointer, indent=2)+"\n", encoding="utf-8")
        os.replace(temporary, root / "data/current.json")
        return pointer
    except Exception as error:
        (snapshot / "FAILED.txt").write_text(str(error), encoding="utf-8")
        raise


def current_snapshot(root: Path = PROJECT_ROOT) -> Path | None:
    pointer = root / "data/current.json"
    if not pointer.is_file():
        return None
    value = json.loads(pointer.read_text(encoding="utf-8"))
    snapshot = (root / value["snapshot"]).resolve()
    if not snapshot.is_relative_to((root / "data/builds").resolve()) or not (snapshot / "status.json").is_file():
        raise ValueError("Invalid current build pointer")
    return snapshot
