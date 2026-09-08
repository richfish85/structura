from __future__ import annotations

import html
import shutil
from pathlib import Path
from urllib.parse import quote

from .db import connect, counts
from .web import safe_external_url


MARKER = ".structura-static-review-site"


def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>{html.escape(title)} · Structura review</title></head>
<body>
<header><h1>Structura review</h1><p>Static, read-only export of non-canonical research intake.</p></header>
<main>{body}</main>
<footer><p>Generated from SQLite. This site does not approve, normalize, or promote records.</p></footer>
</body>
</html>
"""


def _write(root: Path, relative: str, content: str) -> None:
    target = (root / relative).resolve()
    try:
        target.relative_to(root)
    except ValueError as error:
        raise ValueError("static output escaped its requested directory") from error
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")


def _reset_owned_output(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    marker = root / MARKER
    non_marker_entries = [entry for entry in root.iterdir() if entry.name != MARKER]
    if non_marker_entries and not marker.is_file():
        raise ValueError(f"refusing to overwrite a directory not owned by Structura: {root}")
    for name in ("index.html", "batches", "runs", "candidates"):
        target = (root / name).resolve()
        try:
            target.relative_to(root)
        except ValueError as error:
            raise ValueError("static output cleanup escaped its requested directory") from error
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    marker.write_text("Structura static review output v1\n", encoding="utf-8", newline="\n")


def _source_link(title: str, url: str | None) -> str:
    safe_url = safe_external_url(url)
    escaped_title = html.escape(title)
    return f'<a href="{html.escape(safe_url)}" rel="noreferrer">{escaped_title}</a>' if safe_url else escaped_title


def _display_path(value: str | None) -> str:
    """Avoid leaking a workstation's absolute directory into a shareable export."""
    return Path(value).name if value else ""


def _candidate_or_lead_links(candidate_keys: str | None, proposed_keys: str | None) -> str:
    parts = []
    for candidate_key in sorted(set((candidate_keys or "").split(","))):
        if candidate_key:
            path = quote(candidate_key, safe="")
            parts.append(f'<a href="../candidates/{path}.html">{html.escape(candidate_key)}</a>')
    parts.extend(html.escape(key) for key in sorted(set((proposed_keys or "").split(","))) if key)
    return "<br>".join(parts) or "Batch-level finding"


def render_static_site(db_path: Path | str, output_dir: Path | str) -> Path:
    """Create a deterministic, JavaScript-free review site from an SQLite snapshot."""
    root = Path(output_dir).resolve()
    _reset_owned_output(root)
    with connect(db_path, read_only=True) as connection:
        totals = counts(connection)
        batches = connection.execute(
            "SELECT b.id, b.batch_key, b.title, b.scope_note, b.workflow_status, COUNT(DISTINCT r.id) AS run_count, COUNT(DISTINCT c.id) AS candidate_count FROM research_batches b LEFT JOIN research_import_runs r ON r.research_batch_id=b.id LEFT JOIN intake_candidate_records c ON c.import_run_id=r.id GROUP BY b.id ORDER BY b.batch_key"
        ).fetchall()
        batch_rows = []
        for batch in batches:
            path = f"batches/{quote(batch['batch_key'], safe='')}.html"
            batch_rows.append(f"<tr><td><a href=\"{path}\">{html.escape(batch['batch_key'])}</a></td><td>{html.escape(batch['title'])}</td><td>{html.escape(batch['workflow_status'])}</td><td>{batch['run_count']}</td><td>{batch['candidate_count']}</td></tr>")
            runs = connection.execute(
                "SELECT r.*, r.candidate_count AS staged_records FROM research_import_runs r WHERE r.research_batch_id=? ORDER BY r.run_key",
                (batch["id"],),
            ).fetchall()
            candidates = connection.execute(
                "SELECT c.*, e.name, e.record_status, e.confidence, COUNT(v.id) AS verification_count FROM intake_candidate_records c JOIN entities e ON e.id=c.entity_id JOIN research_import_runs r ON r.id=c.import_run_id LEFT JOIN verification_records v ON v.intake_candidate_record_id=c.id WHERE r.research_batch_id=? GROUP BY c.id ORDER BY c.candidate_key",
                (batch["id"],),
            ).fetchall()
            audit_findings = connection.execute(
                "SELECT a.*, GROUP_CONCAT(DISTINCT c.candidate_key) AS affected_candidate_keys, GROUP_CONCAT(DISTINCT p.proposed_candidate_key) AS proposed_candidate_keys FROM audit_findings a JOIN research_import_runs r ON r.id=a.import_run_id LEFT JOIN audit_finding_candidate_refs ar ON ar.audit_finding_id=a.id LEFT JOIN intake_candidate_records c ON c.id=ar.intake_candidate_record_id LEFT JOIN audit_finding_proposed_keys p ON p.audit_finding_id=a.id WHERE r.research_batch_id=? GROUP BY a.id ORDER BY CASE a.severity WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END, a.finding_key",
                (batch["id"],),
            ).fetchall()
            run_rows = "".join(f"<tr><td><a href=\"../runs/{quote(run['run_key'], safe='')}.html\">{html.escape(run['run_key'])}</a></td><td>{html.escape(run['pipeline_stage'])}</td><td>{run['staged_records']}</td><td>{run['source_count']}</td><td><code>{html.escape(run['input_digest'])}</code></td></tr>" for run in runs) or "<tr><td colspan=\"5\">No imported runs.</td></tr>"
            candidate_rows = "".join(f"<tr><td><a href=\"../candidates/{quote(candidate['candidate_key'], safe='')}.html\">{html.escape(candidate['candidate_key'])}</a></td><td>{html.escape(candidate['product_name_raw'])}</td><td>{html.escape(candidate['manufacturer_raw'])}</td><td>{html.escape(candidate['record_status'])}</td><td>{candidate['verification_count']}</td></tr>" for candidate in candidates) or "<tr><td colspan=\"5\">No imported candidates.</td></tr>"
            audit_rows = "".join(
                f"<tr><td><code>{html.escape(row['finding_key'])}</code></td><td>{html.escape(row['finding_type'])}</td><td>{html.escape(row['severity'])}</td><td>{_candidate_or_lead_links(row['affected_candidate_keys'], row['proposed_candidate_keys'])}</td><td>{html.escape(row['finding'])}</td><td>{_source_link('Evidence', row['source_url']) if row['source_url'] else 'Structural finding'}<br>{html.escape(row['source_locator'] or '')}<br>{html.escape(row['source_evidence'] or '')}</td><td>{html.escape(row['recommended_next_action'])}</td><td>{html.escape(row['disposition'])}</td></tr>"
                for row in audit_findings
            ) or "<tr><td colspan=\"8\">No audit findings imported.</td></tr>"
            body = f"<p><a href=\"../index.html\">Batches</a></p><h2>{html.escape(batch['title'])}</h2><dl><dt>Batch key</dt><dd><code>{html.escape(batch['batch_key'])}</code></dd><dt>Workflow status</dt><dd>{html.escape(batch['workflow_status'])}</dd><dt>Scope</dt><dd>{html.escape(batch['scope_note'])}</dd></dl><h3>Import runs</h3><table border=\"1\"><thead><tr><th>Run</th><th>Stage</th><th>Records/findings</th><th>Source URLs</th><th>Input digest</th></tr></thead><tbody>{run_rows}</tbody></table><h3>Candidate records</h3><table border=\"1\"><thead><tr><th>Candidate key</th><th>Raw product name</th><th>Raw manufacturer</th><th>Record status</th><th>Verification assertions</th></tr></thead><tbody>{candidate_rows}</tbody></table><h3>Audit findings and omission leads</h3><p>Proposed keys are leads only; they are not candidate entities.</p><table border=\"1\"><thead><tr><th>Finding</th><th>Type</th><th>Severity</th><th>Affected/proposed key</th><th>Observation</th><th>Evidence</th><th>Next action</th><th>Disposition</th></tr></thead><tbody>{audit_rows}</tbody></table>"
            _write(root, path, _page(batch["title"], body))
        runs = connection.execute("SELECT r.*, b.batch_key FROM research_import_runs r JOIN research_batches b ON b.id=r.research_batch_id ORDER BY r.run_key").fetchall()
        for run in runs:
            source_rows = connection.execute("SELECT s.source_key, s.title, s.url, s.source_tier FROM research_import_run_sources rs JOIN sources s ON s.id=rs.source_id WHERE rs.import_run_id=? ORDER BY s.source_key", (run["id"],)).fetchall()
            source_observations = connection.execute("SELECT source_key_raw, title_raw, publisher_raw, source_type_raw, source_tier_raw, url_raw, publication_date_raw, accessed_date_raw, scope_note_raw FROM intake_source_records WHERE import_run_id=? ORDER BY source_row_number", (run["id"],)).fetchall()
            sources_html = "".join(f"<tr><td>{html.escape(source['source_key'])}</td><td>{_source_link(source['title'], source['url'])}</td><td>{source['source_tier']}</td></tr>" for source in source_rows) or "<tr><td colspan=\"3\">No sources.</td></tr>"
            source_observation_rows = "".join(f"<tr><td>{html.escape(row['source_key_raw'])}</td><td>{_source_link(row['title_raw'], row['url_raw'])}</td><td>{html.escape(row['publisher_raw'] or '')}</td><td>{html.escape(row['source_type_raw'])}</td><td>{row['source_tier_raw']}</td><td>{html.escape(row['publication_date_raw'] or '')}</td><td>{html.escape(row['accessed_date_raw'])}</td><td>{html.escape(row['scope_note_raw'])}</td></tr>" for row in source_observations) or "<tr><td colspan=\"8\">This run has no raw source-register rows.</td></tr>"
            body = f"<p><a href=\"../batches/{quote(run['batch_key'], safe='')}.html\">Batch</a></p><h2>Import run</h2><dl><dt>Run key</dt><dd><code>{html.escape(run['run_key'])}</code></dd><dt>Batch key</dt><dd>{html.escape(run['batch_key'])}</dd><dt>Pipeline stage</dt><dd>{html.escape(run['pipeline_stage'])}</dd><dt>Candidate input</dt><dd><code>{html.escape(_display_path(run['candidate_path']))}</code></dd><dt>Source input</dt><dd><code>{html.escape(_display_path(run['source_path']))}</code></dd><dt>Input digest</dt><dd><code>{html.escape(run['input_digest'])}</code></dd><dt>Importer</dt><dd>{html.escape(run['importer'])}</dd></dl><p>This import remains non-canonical. Source roles and verification findings are shown on candidate pages.</p><h3>Resolved source identities</h3><table border=\"1\"><thead><tr><th>Source key</th><th>Source</th><th>Tier</th></tr></thead><tbody>{sources_html}</tbody></table><h3>Raw source-register hand-off</h3><p>These fields preserve the importing worker's wording even when the source resolved to an existing identity.</p><table border=\"1\"><thead><tr><th>Raw key</th><th>Raw title</th><th>Raw publisher</th><th>Raw type</th><th>Raw tier</th><th>Publication date</th><th>Accessed</th><th>Raw scope note</th></tr></thead><tbody>{source_observation_rows}</tbody></table>"
            _write(root, f"runs/{quote(run['run_key'], safe='')}.html", _page(run["run_key"], body))
        candidates = connection.execute("SELECT c.*, e.entity_key, e.record_status, e.confidence, r.run_key, b.batch_key FROM intake_candidate_records c JOIN entities e ON e.id=c.entity_id JOIN research_import_runs r ON r.id=c.import_run_id JOIN research_batches b ON b.id=r.research_batch_id ORDER BY c.candidate_key").fetchall()
        for candidate in candidates:
            evidence = connection.execute("SELECT s.title, s.url, ee.evidence_role, ee.evidence_note FROM entity_evidence ee JOIN sources s ON s.id=ee.source_id WHERE ee.entity_id=? ORDER BY s.source_key", (candidate["entity_id"],)).fetchall()
            assertions = connection.execute("SELECT v.id AS verification_id, v.identity_status, v.manufacturer_status, v.category_status, v.release_timing_status, v.confidence, v.evidence_role, v.locator, v.evidence_note, v.conflict_note, v.verifier, r.run_key, s.title, s.url FROM verification_records v JOIN research_import_runs r ON r.id=v.import_run_id JOIN sources s ON s.id=v.source_id WHERE v.intake_candidate_record_id=? ORDER BY r.run_key", (candidate["id"],)).fetchall()
            reports = connection.execute("SELECT vr.verified_event_type, vr.verified_timing_raw, vr.date_precision_raw, vr.inclusion_recommendation, vr.source_1_url, vr.source_1_locator, vr.source_1_evidence, vr.source_2_url, vr.source_2_locator, vr.source_2_evidence, vr.unresolved_questions, vr.verifier_notes, r.run_key FROM verification_report_records vr JOIN verification_records v ON v.id=vr.verification_record_id JOIN research_import_runs r ON r.id=v.import_run_id WHERE v.intake_candidate_record_id=? ORDER BY r.run_key", (candidate["id"],)).fetchall()
            normalizations = connection.execute("SELECT n.*, p.candidate_key AS parent_candidate_key, r.run_key FROM normalization_proposals n JOIN research_import_runs r ON r.id=n.import_run_id LEFT JOIN intake_candidate_records p ON p.id=n.parent_intake_candidate_record_id WHERE n.intake_candidate_record_id=? ORDER BY r.run_key", (candidate["id"],)).fetchall()
            candidate_audits = connection.execute("SELECT a.*, r.run_key FROM audit_findings a JOIN research_import_runs r ON r.id=a.import_run_id JOIN audit_finding_candidate_refs ar ON ar.audit_finding_id=a.id WHERE ar.intake_candidate_record_id=? ORDER BY a.finding_key", (candidate["id"],)).fetchall()
            evidence_rows = "".join(f"<tr><td>{_source_link(row['title'], row['url'])}</td><td>{html.escape(row['evidence_role'])}</td><td>{html.escape(row['evidence_note'])}</td></tr>" for row in evidence) or "<tr><td colspan=\"3\">No source references.</td></tr>"
            assertion_rows = "".join(f"<tr><td><a href=\"../runs/{quote(row['run_key'], safe='')}.html\">{html.escape(row['run_key'])}</a></td><td>{html.escape(row['identity_status'])}</td><td>{html.escape(row['manufacturer_status'])}</td><td>{html.escape(row['category_status'])}</td><td>{html.escape(row['release_timing_status'])}</td><td>{html.escape(row['confidence'])}</td><td>{_source_link(row['title'], row['url'])}<br>{html.escape(row['evidence_role'])}<br>{html.escape(row['locator'] or '')}<br>{html.escape(row['evidence_note'])}<br>{html.escape(row['conflict_note'] or '')}<br>Verifier: {html.escape(row['verifier'])}</td></tr>" for row in assertions) or "<tr><td colspan=\"7\">No verification assertions imported.</td></tr>"
            report_rows = "".join(f"<tr><td><a href=\"../runs/{quote(row['run_key'], safe='')}.html\">{html.escape(row['run_key'])}</a></td><td>{html.escape(row['verified_event_type'])}</td><td>{html.escape(row['verified_timing_raw'])}</td><td>{html.escape(row['date_precision_raw'])}</td><td>{html.escape(row['inclusion_recommendation'])}</td><td>{_source_link('Source 1', row['source_1_url'])}<br>{html.escape(row['source_1_locator'] or '')}<br>{html.escape(row['source_1_evidence'])}<br>{_source_link('Source 2', row['source_2_url']) if row['source_2_url'] else ''}<br>{html.escape(row['source_2_locator'] or '')}<br>{html.escape(row['source_2_evidence'] or '')}</td><td>{html.escape(row['unresolved_questions'] or '')}<br>{html.escape(row['verifier_notes'])}</td></tr>" for row in reports)
            raw_rows = "".join(f"<tr><th>{html.escape(label)}</th><td>{html.escape(candidate[column] or '')}</td></tr>" for label, column in (("Raw manufacturer", "manufacturer_raw"), ("Raw product name", "product_name_raw"), ("Raw model number", "model_number_raw"), ("Raw product type", "product_type_raw"), ("Raw announcement date", "announced_date_raw"), ("Raw release date", "release_date_raw"), ("Raw market scope", "market_scope_raw"), ("Notes", "notes")))
            report_table = f"<h3>Verification report detail</h3><table border=\"1\"><thead><tr><th>Run</th><th>Verified event</th><th>Verified timing (raw)</th><th>Raw date precision</th><th>Inclusion recommendation</th><th>Source evidence</th><th>Open questions / verifier notes</th></tr></thead><tbody>{report_rows}</tbody></table>" if report_rows else ""
            normalization_rows = "".join(f"<tr><td><a href=\"../runs/{quote(row['run_key'], safe='')}.html\">{html.escape(row['run_key'])}</a></td><td>{html.escape(row['normalized_display_name'])}</td><td>{html.escape(row['normalized_manufacturer'])}</td><td>{html.escape(row['entity_granularity'])}</td><td>{html.escape(row['parent_candidate_key'] or '')}</td><td>{html.escape(row['normalized_category'])}</td><td>{html.escape(row['qualifying_event_type'])}<br>{html.escape(row['normalized_launch_date'] or '')} ({html.escape(row['date_precision'])})</td><td>{html.escape(row['decision_status'])}</td><td>{html.escape(row['rationale'])}<br>{html.escape(row['open_questions'] or '')}</td></tr>" for row in normalizations) or "<tr><td colspan=\"9\">No normalization proposal imported.</td></tr>"
            audit_rows = "".join(f"<tr><td><a href=\"../runs/{quote(row['run_key'], safe='')}.html\">{html.escape(row['run_key'])}</a></td><td>{html.escape(row['finding_type'])}</td><td>{html.escape(row['severity'])}</td><td>{html.escape(row['finding'])}</td><td>{_source_link('Evidence', row['source_url']) if row['source_url'] else 'Structural finding'}<br>{html.escape(row['source_evidence'] or '')}</td><td>{html.escape(row['recommended_next_action'])}</td><td>{html.escape(row['disposition'])}</td></tr>" for row in candidate_audits) or "<tr><td colspan=\"7\">No audit findings for this candidate.</td></tr>"
            body = f"<p><a href=\"../batches/{quote(candidate['batch_key'], safe='')}.html\">Batch</a> · <a href=\"../runs/{quote(candidate['run_key'], safe='')}.html\">Scout import run</a></p><h2>{html.escape(candidate['product_name_raw'])}</h2><p>Candidate key: <code>{html.escape(candidate['candidate_key'])}</code><br>Record status: {html.escape(candidate['record_status'])}<br>Confidence: {html.escape(candidate['confidence'])}</p><p>These fields are raw intake. They are not normalized findings.</p><h3>Raw hand-off</h3><table border=\"1\"><tbody>{raw_rows}</tbody></table><h3>Source references</h3><table border=\"1\"><thead><tr><th>Source</th><th>Role</th><th>Note</th></tr></thead><tbody>{evidence_rows}</tbody></table><h3>Verification assertions</h3><p>Assertions below record a verifier's assessment; they do not change the candidate or canonical status.</p><table border=\"1\"><thead><tr><th>Verification run</th><th>Identity</th><th>Manufacturer</th><th>Category</th><th>Release timing</th><th>Confidence</th><th>Evidence</th></tr></thead><tbody>{assertion_rows}</tbody></table>{report_table}<h3>Normalization proposal</h3><p>Proposed labels and hierarchy below do not rewrite the raw record.</p><table border=\"1\"><thead><tr><th>Run</th><th>Display name</th><th>Manufacturer</th><th>Granularity</th><th>Parent</th><th>Category</th><th>Qualifying event</th><th>Decision</th><th>Rationale / questions</th></tr></thead><tbody>{normalization_rows}</tbody></table><h3>Audit findings</h3><table border=\"1\"><thead><tr><th>Run</th><th>Type</th><th>Severity</th><th>Finding</th><th>Evidence</th><th>Next action</th><th>Disposition</th></tr></thead><tbody>{audit_rows}</tbody></table>"
            _write(root, f"candidates/{quote(candidate['candidate_key'], safe='')}.html", _page(candidate["product_name_raw"], body))
    overview_rows = "".join(batch_rows) or "<tr><td colspan=\"5\">No batches.</td></tr>"
    body = f"<h2>Review batches</h2><p>Entities: {totals['entities']}; sources: {totals['sources']}; import runs are listed by batch below.</p><p>This is a static review export. It contains raw agent hand-offs, not a canonical census.</p><table border=\"1\"><thead><tr><th>Batch key</th><th>Title</th><th>Workflow status</th><th>Runs</th><th>Candidates</th></tr></thead><tbody>{overview_rows}</tbody></table>"
    _write(root, "index.html", _page("Batches", body))
    return root
