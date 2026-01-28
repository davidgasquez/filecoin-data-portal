from __future__ import annotations

import argparse
from pathlib import Path

from fdp.materialize import materialize


def main() -> None:
    parser = argparse.ArgumentParser(prog="fdp")
    subparsers = parser.add_subparsers(dest="command", required=True)

    materialize_parser = subparsers.add_parser(
        "materialize",
        help="Materialize datasets into DuckDB.",
    )
    materialize_parser.add_argument(
        "datasets",
        nargs="*",
        help="Dataset names to materialize.",
    )
    materialize_parser.add_argument(
        "--all",
        action="store_true",
        help="Materialize all datasets.",
    )
    materialize_parser.add_argument(
        "--db-path",
        default="fdp.duckdb",
        help="DuckDB database path.",
    )

    args = parser.parse_args()

    if args.command == "materialize":
        if not args.all and not args.datasets:
            parser.error("Pass --all or dataset names.")
        materialize(
            args.datasets,
            all_datasets=args.all,
            db_path=Path(args.db_path),
        )
