import argparse
import json
import os
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import duckdb

DATABASE_PATH_ENV = "DATABASE_PATH"
MOTHERDUCK_TOKEN_ENV = "motherduck_token"
MOTHERDUCK_TOKEN_ENV_FALLBACK = "MOTHERDUCK_TOKEN"
DEFAULT_FETCH_SIZE = 1_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a SQL query against the MotherDuck database and print rows as JSON lines."
    )
    parser.add_argument("query", nargs="?", help="SQL query string")
    parser.add_argument(
        "--file",
        type=Path,
        help="Read SQL query from file",
    )
    parser.add_argument(
        "--database",
        default=os.getenv(DATABASE_PATH_ENV),
        help=f"DuckDB database path or MotherDuck URI (default: ${DATABASE_PATH_ENV})",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        help="Maximum number of rows to return",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output",
    )
    parser.add_argument(
        "--read-only",
        action="store_true",
        help="Open DuckDB connection in read-only mode",
    )
    return parser.parse_args()


def load_query(args: argparse.Namespace) -> str:
    if args.query and args.file:
        raise SystemExit("Pass either a query argument or --file, not both")

    raw_query: str | None = None
    if args.query:
        raw_query = args.query
    elif args.file:
        raw_query = args.file.read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        raw_query = sys.stdin.read()

    if raw_query is None:
        raise SystemExit("Query is required. Pass it as an argument, --file, or stdin")

    query = raw_query.strip()
    if not query:
        raise SystemExit("Query is empty")

    return query


def resolve_motherduck_token() -> str | None:
    token = os.getenv(MOTHERDUCK_TOKEN_ENV)
    if token and token.strip():
        return token

    fallback = os.getenv(MOTHERDUCK_TOKEN_ENV_FALLBACK)
    if fallback and fallback.strip():
        return fallback

    return None


def load_database(args: argparse.Namespace) -> str:
    if args.database is None or not args.database.strip():
        raise SystemExit(
            f"Database is required. Set --database or ${DATABASE_PATH_ENV}"
        )

    database = args.database.strip()
    token = resolve_motherduck_token()
    if database.startswith("md:") and token is None:
        raise SystemExit(
            "MotherDuck token is required. Set motherduck_token or MOTHERDUCK_TOKEN"
        )

    return database


def load_columns(cursor: duckdb.DuckDBPyConnection) -> list[str]:
    description = cursor.description or []
    return [column[0] for column in description]


def iter_rows(
    cursor: duckdb.DuckDBPyConnection, max_results: int | None
) -> Iterator[tuple[object, ...]]:
    remaining = max_results

    while True:
        chunk_size = DEFAULT_FETCH_SIZE
        if remaining is not None:
            if remaining <= 0:
                return
            chunk_size = min(chunk_size, remaining)

        chunk = cursor.fetchmany(chunk_size)
        if not chunk:
            return

        for row in chunk:
            yield row

        if remaining is not None:
            remaining -= len(chunk)


def run_query(args: argparse.Namespace, query: str) -> int:
    if args.max_results is not None and args.max_results < 0:
        raise SystemExit("--max-results must be >= 0")

    database = load_database(args)
    token = resolve_motherduck_token()
    config: dict[str, str | bool | int | float | list[str]] | None = None
    if token:
        config = {"motherduck_token": token}

    indent = 2 if args.pretty else None
    row_count = 0
    started_at = time.perf_counter()

    with duckdb.connect(
        database=database, config=config, read_only=args.read_only
    ) as conn:
        cursor = conn.execute(query)
        columns = load_columns(cursor)
        for row in iter_rows(cursor, args.max_results):
            payload = dict(zip(columns, row, strict=True))
            print(json.dumps(payload, default=str, indent=indent))
            row_count += 1

    elapsed_seconds = round(time.perf_counter() - started_at, 3)
    summary = {
        "rows": row_count,
        "database": database,
        "max_results": args.max_results,
        "elapsed_seconds": elapsed_seconds,
    }
    print(json.dumps(summary), file=sys.stderr)
    return 0


def main() -> int:
    args = parse_args()
    query = load_query(args)
    return run_query(args, query)


if __name__ == "__main__":
    raise SystemExit(main())
