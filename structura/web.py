from __future__ import annotations

import html
import json
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse
from wsgiref.simple_server import make_server

from .db import connect, counts


STYLE = """
body { background: #f3f3f3; color: #161616; font: 16px/1.5 Georgia, serif; margin: 0; }
header, main, footer { box-sizing: border-box; margin: auto; max-width: 980px; padding: 18px 24px; }
header { background: #fff; border-bottom: 1px solid #aaa; }
h1, h2, h3 { font-family: Arial, sans-serif; }
h1 { margin: 0; }
a { color: #0645ad; }
nav { margin-top: 8px; }
table { background: #fff; border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #bbb; padding: 8px; text-align: left; vertical-align: top; }
th { background: #e6e6e6; font-family: Arial, sans-serif; }
.notice { background: #fff8d8; border: 1px solid #c8b45d; padding: 10px 12px; }
.muted { color: #666; }
.stats { display: flex; flex-wrap: wrap; gap: 12px; padding: 0; }
.stats li { background: #fff; border: 1px solid #bbb; list-style: none; padding: 10px 14px; }
label { display: inline-block; margin-right: 12px; }
input, select, button { font: inherit; }
footer { color: #555; font-size: 14px; }
"""


def page(title: str, body: str) -> bytes:
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} · Structura</title>
  <style>{STYLE}</style>
</head>
<body>
  <header><h1><a href="/">Structura</a></h1><div>HardwareDB local explorer</div><nav><a href="/entities">Entities</a> · <a href="/health">Health</a></nav></header>
  <main><p class="notice"><strong>Local foundation:</strong> proposed ontology, incomplete data, and no public completeness claim.</p>{body}</main>
  <footer>Read-only inspection interface · canonical data remains in SQLite</footer>
</body>
</html>"""
    return document.encode("utf-8")


def safe_external_url(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlparse(value)
    return value if parsed.scheme in {"http", "https"} and parsed.netloc else None


def respond(start_response, status: str, content_type: str, content: bytes):
    start_response(
        status,
        [
            ("Content-Type", content_type),
            ("Content-Length", str(len(content))),
            ("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'self'"),
            ("Referrer-Policy", "no-referrer"),
            ("X-Content-Type-Options", "nosniff"),
        ],
    )
    return [content]


def create_app(db_path: Path | str):
    path = Path(db_path).resolve()

    def app(environ, start_response):
        request = urlparse(environ.get("PATH_INFO", "/"))

        if request.path == "/health":
            with connect(path, read_only=True) as connection:
                payload = {"status": "ok", "database": str(path), "counts": counts(connection)}
            content = json.dumps(payload, indent=2).encode("utf-8")
            return respond(start_response, "200 OK", "application/json; charset=utf-8", content)

        if request.path == "/":
            with connect(path, read_only=True) as connection:
                totals = counts(connection)
                batches = connection.execute(
                    "SELECT title, scope_note, workflow_status FROM research_batches ORDER BY id"
                ).fetchall()
            stat_items = "".join(
                f"<li><strong>{value}</strong><br>{html.escape(name.replace('_', ' ').title())}</li>"
                for name, value in totals.items()
            )
            batch_rows = "".join(
                f"<tr><td>{html.escape(row['title'])}</td><td>{html.escape(row['scope_note'])}</td><td>{html.escape(row['workflow_status'])}</td></tr>"
                for row in batches
            ) or '<tr><td colspan="3">No research batches.</td></tr>'
            body = f"<h2>Database overview</h2><ul class='stats'>{stat_items}</ul><h2>Research batches</h2><table><thead><tr><th>Batch</th><th>Scope</th><th>Status</th></tr></thead><tbody>{batch_rows}</tbody></table>"
            return respond(start_response, "200 OK", "text/html; charset=utf-8", page("Overview", body))

        if request.path == "/entities":
            query = parse_qs(environ.get("QUERY_STRING", ""))
            search = query.get("q", [""])[0].strip()
            status_filter = query.get("status", [""])[0].strip()
            clauses = []
            params: list[str] = []
            if search:
                clauses.append("(e.name LIKE ? OR e.entity_key LIKE ?)")
                params.extend([f"%{search}%", f"%{search}%"])
            if status_filter:
                clauses.append("e.record_status = ?")
                params.append(status_filter)
            where = " WHERE " + " AND ".join(clauses) if clauses else ""
            with connect(path, read_only=True) as connection:
                rows = connection.execute(
                    "SELECT e.entity_key, e.name, et.label AS entity_type, e.record_status, e.confidence "
                    "FROM entities e JOIN entity_types et ON et.code = e.entity_type_code"
                    + where
                    + " ORDER BY e.name LIMIT 500",
                    params,
                ).fetchall()
            result_rows = "".join(
                f"<tr><td><a href='/entities/{quote(row['entity_key'], safe='')}'>{html.escape(row['name'])}</a></td><td>{html.escape(row['entity_type'])}</td><td>{html.escape(row['record_status'])}</td><td>{html.escape(row['confidence'])}</td></tr>"
                for row in rows
            ) or '<tr><td colspan="4">No matching entities.</td></tr>'
            body = f"""<h2>Entities</h2>
<form method="get"><label>Search <input name="q" value="{html.escape(search)}"></label><label>Status <select name="status"><option value="">Any</option>{''.join(f'<option value="{value}" {"selected" if status_filter == value else ""}>{value}</option>' for value in ('candidate', 'verified', 'review_required', 'canonical', 'retired', 'example'))}</select></label><button>Filter</button></form>
<p class="muted">At most 500 records are shown.</p>
<table><thead><tr><th>Name</th><th>Type</th><th>Status</th><th>Confidence</th></tr></thead><tbody>{result_rows}</tbody></table>"""
            return respond(start_response, "200 OK", "text/html; charset=utf-8", page("Entities", body))

        if request.path.startswith("/entities/"):
            entity_key = unquote(request.path.removeprefix("/entities/"))
            with connect(path, read_only=True) as connection:
                entity = connection.execute(
                    "SELECT e.*, et.label AS entity_type FROM entities e JOIN entity_types et ON et.code=e.entity_type_code WHERE e.entity_key=?",
                    (entity_key,),
                ).fetchone()
                if entity is None:
                    return respond(start_response, "404 Not Found", "text/html; charset=utf-8", page("Not found", "<h2>Entity not found</h2>"))
                outgoing = connection.execute(
                    "SELECT p.label, o.entity_key, o.name, r.assertion_status, r.confidence FROM relationships r JOIN predicates p ON p.code=r.predicate_code JOIN entities o ON o.id=r.object_id WHERE r.subject_id=? ORDER BY p.label, o.name",
                    (entity["id"],),
                ).fetchall()
                evidence = connection.execute(
                    "SELECT ee.field_name, ee.evidence_role, ee.locator, ee.evidence_note, s.title, s.publisher, s.url, s.archive_url, s.source_tier FROM entity_evidence ee JOIN sources s ON s.id=ee.source_id WHERE ee.entity_id=? ORDER BY s.source_tier, s.title",
                    (entity["id"],),
                ).fetchall()
            relationship_rows = "".join(
                f"<tr><td>{html.escape(row['label'])}</td><td><a href='/entities/{quote(row['entity_key'], safe='')}'>{html.escape(row['name'])}</a></td><td>{html.escape(row['assertion_status'])}</td><td>{html.escape(row['confidence'])}</td></tr>"
                for row in outgoing
            ) or '<tr><td colspan="4">No outgoing relationships.</td></tr>'
            evidence_cells = []
            for row in evidence:
                source_url = safe_external_url(row["url"] or row["archive_url"])
                source_title = html.escape(row["title"])
                source_display = (
                    f"<a href='{html.escape(source_url)}' rel='noreferrer'>{source_title}</a>"
                    if source_url
                    else source_title
                )
                evidence_cells.append(
                    f"<tr><td>{html.escape(row['field_name'])}</td><td>{html.escape(row['evidence_role'])}</td><td>{source_display}<br><span class='muted'>Tier {row['source_tier']} · {html.escape(row['publisher'] or 'publisher unknown')}</span></td><td>{html.escape(row['locator'] or '')}<br>{html.escape(row['evidence_note'])}</td></tr>"
                )
            evidence_rows = "".join(evidence_cells) or '<tr><td colspan="4">No entity evidence.</td></tr>'
            body = f"<p><a href='/entities'>← Entities</a></p><h2>{html.escape(entity['name'])}</h2><dl><dt>Key</dt><dd>{html.escape(entity['entity_key'])}</dd><dt>Type</dt><dd>{html.escape(entity['entity_type'])}</dd><dt>Status</dt><dd>{html.escape(entity['record_status'])}</dd><dt>Confidence</dt><dd>{html.escape(entity['confidence'])}</dd></dl><p>{html.escape(entity['description'] or '')}</p><h3>Relationships</h3><table><thead><tr><th>Predicate</th><th>Object</th><th>Status</th><th>Confidence</th></tr></thead><tbody>{relationship_rows}</tbody></table><h3>Evidence</h3><table><thead><tr><th>Field</th><th>Role</th><th>Source</th><th>Locator / note</th></tr></thead><tbody>{evidence_rows}</tbody></table>"
            return respond(start_response, "200 OK", "text/html; charset=utf-8", page(entity["name"], body))

        return respond(start_response, "404 Not Found", "text/html; charset=utf-8", page("Not found", "<h2>Page not found</h2>"))

    return app


def serve(db_path: Path | str, *, host: str = "127.0.0.1", port: int = 8000) -> None:
    path = Path(db_path).resolve()
    print(f"Structura explorer: http://{host}:{port}")
    print(f"Database: {path}")
    with make_server(host, port, create_app(path)) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStructura explorer stopped.")
