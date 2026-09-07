from __future__ import annotations

import argparse
from pathlib import Path

from .db import DEFAULT_DB, connect, counts, initialize, validate
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

    return 2
