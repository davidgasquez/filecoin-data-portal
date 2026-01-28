from __future__ import annotations

import argparse
import sys
from fdp.materialize import materialize

SHORT_HELP = """Filecoin Data Portal CLI.

Usage:
  fdp materialize --all
  fdp materialize DATASET [DATASET...]

Run "fdp --help" for more.
"""


def _materialize(args: argparse.Namespace) -> None:
    if not args.all and not args.datasets:
        raise SystemExit(
            "Usage: fdp materialize [--all] [DATASET...]\n"
            "\n"
            "Pass --all or dataset names. "
            "Run 'fdp materialize --help' for more."
        )
    materialize(
        args.datasets,
        all_datasets=args.all,
    )


def main() -> None:
    if len(sys.argv) == 1:
        print(SHORT_HELP)
        raise SystemExit(0)

    parser = argparse.ArgumentParser(
        prog="fdp",
        description="Filecoin Data Portal CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    materialize_parser = subparsers.add_parser(
        "materialize",
        help="Materialize datasets into DuckDB.",
    )
    materialize_parser.add_argument(
        "datasets",
        nargs="*",
        metavar="DATASET",
        help="Dataset names to materialize.",
    )
    materialize_parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Materialize all datasets.",
    )
    materialize_parser.set_defaults(func=_materialize)

    args = parser.parse_args()
    args.func(args)
