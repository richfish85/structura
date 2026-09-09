from __future__ import annotations

import argparse
from pathlib import Path

from .db import DEFAULT_DB, connect, counts, initialize, validate
from .intake import (
    IntakeError,
    import_audit,
    import_batch,
    import_context,
    import_normalization,
    import_review_decisions,
    import_verification,
)
from .static_site import render_static_site
from .web import serve


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="structura",
        description="Local tools for the Structura hardware knowledge base.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("build", help="Rebuild the complete current reference from frozen research packets.")

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
    serve_parser.add_argument("--review", action="store_true", help="Use the legacy SQL review interface.")

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

    review_parser = subparsers.add_parser(
        "import-review-decisions",
        help="Load append-only non-canonical candidate discrepancy review decisions.",
    )
    review_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    review_parser.add_argument("--decisions", type=Path, required=True)

    context_parser = subparsers.add_parser(
        "import-context",
        help="Load non-canonical product-purpose and benchmark evidence.",
    )
    context_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    context_parser.add_argument("--intent", type=Path, required=True)
    context_parser.add_argument("--benchmarks", type=Path, required=True)
    context_parser.add_argument("--sources", type=Path, required=True)

    render_parser = subparsers.add_parser("render-review", help="Render a static HTML review site from SQLite.")
    render_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    render_parser.add_argument("--output", type=Path, required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "build":
        from .build import build
        try:
            result = build()
        except (ValueError, OSError) as error:
            print(f"Build failed; current checkpoint unchanged: {error}")
            return 1
        status = result["status"]
        print("Structura build passed")
        for cohort in status["cohorts"]:
            print(f"  {cohort['batch_key']}: {cohort['candidates']} candidates")
        for key in ("canonical_entities", "relationships", "audit_findings", "reviewed_candidates"):
            print(f"  {key.replace('_', ' ')}: {status[key]}")
        print("Real-person usability trial: pending")
        print("Run python -m structura serve to open the current reference.")
        return 0

    if args.command != "init":
        from .build import current_snapshot
        current = current_snapshot()
        if current is not None and args.db == DEFAULT_DB:
            args.db = current / "structura.db"
        if args.command == "serve" and current is not None and not args.review and args.db == current / "structura.db":
            from .explorer import serve_explorer
            serve_explorer(current / "site", host=args.host, port=args.port, follow_current=True)
            return 0

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

    if args.command == "import-review-decisions":
        try:
            result = import_review_decisions(args.db, args.decisions)
        except IntakeError as error:
            print(f"Review decisions rejected: {error}")
            return 1
        if result.already_imported:
            print(f"Review decisions already imported without duplication: {result.run_key}")
        else:
            print(f"Imported non-canonical review decision run: {result.run_key} ({result.candidate_count} decisions)")
        return 0

    if args.command == "import-context":
        try:
            result = import_context(args.db, args.intent, args.benchmarks, args.sources)
        except IntakeError as error:
            print(f"Context import rejected: {error}")
            return 1
        if result.already_imported:
            print(f"Context already imported without duplication: {result.run_key}")
        else:
            print(
                "Imported non-canonical context run: "
                f"{result.run_key} ({result.intent_count} intent claims, "
                f"{result.benchmark_count} benchmark observations, "
                f"{result.source_count} sources)"
            )
        return 0

    return 2
