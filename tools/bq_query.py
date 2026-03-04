import argparse
import base64
import binascii
import json
import os
import sys
from pathlib import Path

from google.auth.credentials import Credentials
from google.cloud import bigquery
from google.oauth2 import service_account

ENCODED_CREDENTIALS_ENV = "ENCODED_GOOGLE_APPLICATION_CREDENTIALS"
DEFAULT_MAX_BYTES_PROCESSED = 300 * 1024**3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a BigQuery SQL query and print rows as JSON lines."
    )
    parser.add_argument("query", nargs="?", help="SQL query string")
    parser.add_argument("--file", type=Path, help="Path to a .sql file")
    parser.add_argument("--project", help="GCP project used for query job billing")
    parser.add_argument("--location", help="BigQuery location, for example US or EU")
    parser.add_argument(
        "--max-results", type=int, help="Maximum number of rows to return"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate query and print estimated bytes processed",
    )
    parser.add_argument(
        "--max-bytes-processed",
        type=int,
        default=DEFAULT_MAX_BYTES_PROCESSED,
        help="Refuse execution above this estimated scan size in bytes (default: 300 GiB)",
    )
    parser.add_argument(
        "--allow-large-scan",
        action="store_true",
        help="Allow execution even if estimated bytes processed exceed the threshold",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output",
    )
    return parser.parse_args()


def load_query(args: argparse.Namespace) -> str:
    if args.query and args.file:
        raise SystemExit("Pass either a query argument or --file, not both")

    if args.file:
        query = args.file.read_text(encoding="utf-8")
    elif args.query:
        query = args.query
    elif not sys.stdin.isatty():
        query = sys.stdin.read()
    else:
        raise SystemExit("No query provided. Use argument, --file, or stdin")

    query = query.strip()
    if not query:
        raise SystemExit("Query is empty")

    return query


def load_credentials() -> Credentials | None:
    encoded = os.getenv(ENCODED_CREDENTIALS_ENV)

    if encoded is None:
        dotenv_path = Path(".env")
        if dotenv_path.exists():
            for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line.removeprefix("export ").strip()
                if "=" not in line:
                    continue

                name, value = line.split("=", 1)
                if name.strip() != ENCODED_CREDENTIALS_ENV:
                    continue

                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                    value = value[1:-1]
                encoded = value
                break

    if encoded is None:
        return None

    if not encoded.strip():
        raise SystemExit(f"{ENCODED_CREDENTIALS_ENV} is empty")

    try:
        decoded_bytes = base64.b64decode(encoded)
        payload = json.loads(decoded_bytes.decode("utf-8"))
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
        try:
            payload = json.loads(encoded)
        except json.JSONDecodeError as exc:
            raise SystemExit(
                f"{ENCODED_CREDENTIALS_ENV} must contain base64 or JSON service account credentials"
            ) from exc

    if not isinstance(payload, dict):
        raise SystemExit("Decoded credentials payload must be a JSON object")

    try:
        return service_account.Credentials.from_service_account_info(payload)
    except Exception as exc:
        raise SystemExit(
            f"Invalid service account credentials in {ENCODED_CREDENTIALS_ENV}"
        ) from exc


def format_bytes(value: int | None) -> str:
    if value is None:
        return "unknown"
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{value} B"


def run_query(args: argparse.Namespace, query: str) -> int:
    credentials = load_credentials()
    project = args.project
    if project is None and credentials is not None:
        maybe_project = getattr(credentials, "project_id", None)
        if isinstance(maybe_project, str):
            project = maybe_project

    client = bigquery.Client(
        project=project,
        location=args.location,
        credentials=credentials,
    )

    estimate_job = client.query(
        query,
        job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False),
    )
    estimated_bytes = int(estimate_job.total_bytes_processed or 0)
    statement_type = estimate_job.statement_type

    if args.dry_run:
        payload = {
            "dry_run": True,
            "bytes_processed": estimated_bytes,
            "bytes_processed_human": format_bytes(estimated_bytes),
            "statement_type": statement_type,
            "max_bytes_processed": args.max_bytes_processed,
            "max_bytes_processed_human": format_bytes(args.max_bytes_processed),
            "blocked_by_default_limit": estimated_bytes > args.max_bytes_processed,
        }
        print(json.dumps(payload))
        return 0

    if not args.allow_large_scan and estimated_bytes > args.max_bytes_processed:
        advice = (
            "Refusing to run query. Estimated scan is "
            f"{format_bytes(estimated_bytes)} ({estimated_bytes} bytes), above limit "
            f"{format_bytes(args.max_bytes_processed)} ({args.max_bytes_processed} bytes). "
            "Check table partitions and filter on partition columns like _PARTITIONDATE, "
            "_PARTITIONTIME, or date keys. Use --dry-run to inspect. "
            "If intentional, raise --max-bytes-processed or pass --allow-large-scan."
        )
        raise SystemExit(advice)

    job_config = None
    if not args.allow_large_scan:
        job_config = bigquery.QueryJobConfig(
            maximum_bytes_billed=args.max_bytes_processed
        )

    job = client.query(query, job_config=job_config)
    rows = job.result(max_results=args.max_results)

    indent = 2 if args.pretty else None
    row_count = 0
    for row in rows:
        row_count += 1
        print(json.dumps(dict(row.items()), default=str, indent=indent))

    summary = {
        "rows": row_count,
        "estimated_bytes_processed": estimated_bytes,
        "estimated_bytes_processed_human": format_bytes(estimated_bytes),
        "bytes_processed": job.total_bytes_processed,
        "bytes_processed_human": format_bytes(job.total_bytes_processed),
        "job_id": job.job_id,
    }
    print(json.dumps(summary), file=sys.stderr)
    return 0


def main() -> int:
    args = parse_args()
    if args.max_bytes_processed < 0:
        raise SystemExit("--max-bytes-processed must be >= 0")
    query = load_query(args)
    return run_query(args, query)


if __name__ == "__main__":
    raise SystemExit(main())
