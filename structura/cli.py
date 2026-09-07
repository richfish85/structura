from __future__ import annotations

import argparse
from pathlib import Path

from .db import DEFAULT_DB, connect, counts, initialize, validate
from .intake import IntakeError, import_audit, import_batch, import_normalization, import_verification
from .static_site import render_static_site
from .web import serve


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="structura",
        description="Local tools for the Structura hardware knowledge base.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create or migrate a local SQLite database.")
    init_parser.add_argument("--db", type=Path, default=DEFAULT_DB)

    stats_parser = subparsers.add_parser("stats", help="Show record counts.")
    stats_parser.add_argument("--db", type=Path, default=DEFAULT_DB)

    check_parser = subparsers.add_parser("check", help="Validate integrity and canonical evidence gates.")
    check_parser.add_argument("--db", type=Path, default=DEFAULT_DB)

    serve_parser = subparsers.add_parser("serve", help="Run the read-only local HTML explorer.")
    serve_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)

    import_parser = subparsers.add_parser("import-batch", help="Load one non-canonical research hand-off into SQLite.")
    import_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    import_parser.add_argument("--candidates", type=Path, required=True)
    import_parser.add_argument("--sources", type=Path, required=True)
    import_parser.add_argument("--stage", default="scouting")

    verification_parser = subparsers.add_parser("import-verification", help="Load a non-canonical verification assertion hand-off.")
    verification_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    verification_parser.add_argument("--verification", type=Path, required=True)

    normalization_parser = subparsers.add_parser("import-normalization", help="Load non-canonical normalization proposals.")
    normalization_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    normalization_parser.add_argument("--normalization", type=Path, required=True)

    audit_parser = subparsers.add_parser("import-audit", help="Load non-canonical audit findings and omission leads.")
    audit_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    audit_parser.add_argument("--audit", type=Path, required=True)

    render_parser = subparsers.add_parser("render-review", help="Render a static HTML review site from SQLite.")
    render_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    render_parser.add_argument("--output", type=Path, required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "init":
        path = initialize(args.db)
        print(f"Structura database ready: {path}")
        return 0

    if not args.db.exists():
        print(f"Database not found: {args.db.resolve()}")
        print("Run `python -m structura init` first.")
        return 2

    if args.command == "stats":
        with connect(args.db, read_only=True) as connection:
            for name, value in counts(connection).items():
                print(f"{name}: {value}")
        return 0

    if args.command == "check":
        with connect(args.db, read_only=True) as connection:
            problems = validate(connection)
        if problems:
            print("Validation failed:")
            for problem in problems:
                print(f"- {problem}")
            return 1
        print("Validation passed: foreign keys are intact and canonical records have supporting evidence.")
        return 0

    if args.command == "serve":
        serve(args.db, host=args.host, port=args.port)
        return 0

    if args.command == "import-batch":
        if not args.db.exists():
            print(f"Database not found: {args.db.resolve()}")
            print("Run `python -m structura init` first.")
            return 2
        try:
            result = import_batch(args.db, args.candidates, args.sources, stage=args.stage)
        except IntakeError as error:
            print(f"Import rejected: {error}")
            return 1
        if result.already_imported:
            print(f"Batch already imported without duplication: {result.run_key}")
        else:
            print(f"Imported non-canonical run: {result.run_key} ({result.candidate_count} candidates, {result.source_count} sources)")
        return 0

    if args.command == "render-review":
        if not args.db.exists():
            print(f"Database not found: {args.db.resolve()}")
            print("Run `python -m structura init` first.")
            return 2
        try:
            path = render_static_site(args.db, args.output)
        except ValueError as error:
            print(f"Render rejected: {error}")
            return 1
        print(f"Static review site written: {path}")
        return 0

    if args.command == "import-verification":
        if not args.db.exists():
            print(f"Database not found: {args.db.resolve()}")
            print("Run `python -m structura init` and import the scout batch first.")
            return 2
        try:
            result = import_verification(args.db, args.verification)
        except IntakeError as error:
            print(f"Verification import rejected: {error}")
            return 1
        if result.already_imported:
            print(f"Verification already imported without duplication: {result.run_key}")
        else:
            print(f"Imported non-canonical verification run: {result.run_key} ({result.candidate_count} assertions, {result.source_count} registered sources)")
        return 0

    if args.command == "import-normalization":
        try:
            result = import_normalization(args.db, args.normalization)
        except IntakeError as error:
            print(f"Normalization import rejected: {error}")
            return 1
        if result.already_imported:
            print(f"Normalization already imported without duplication: {result.run_key}")
        else:
            print(f"Imported non-canonical normalization run: {result.run_key} ({result.candidate_count} proposals)")
        return 0

    if args.command == "import-audit":
        try:
            result = import_audit(args.db, args.audit)
        except IntakeError as error:
            print(f"Audit import rejected: {error}")
            return 1
        if result.already_imported:
            print(f"Audit already imported without duplication: {result.run_key}")
        else:
            print(f"Imported non-canonical audit run: {result.run_key} ({result.candidate_count} findings, {result.source_count} source URLs)")
        return 0

    return 2
