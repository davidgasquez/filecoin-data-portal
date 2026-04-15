import argparse

from fdp.api import db_connection, find_project_root
from fdp.assets import check_assets, discover_assets
from fdp.docs import generate_docs
from fdp.materialize import materialize
from fdp.publish import available_targets, publish
from fdp.show import show_asset
from fdp.status import prune_tables, show_status
from fdp.test import test_assets


def _materialize(args: argparse.Namespace) -> None:
    materialize(args.selectors, include_dependencies=args.with_deps)


def _check(_: argparse.Namespace) -> None:
    check_assets()


def _list_assets(_: argparse.Namespace) -> None:
    project_root = find_project_root()
    assets = discover_assets()
    if not assets:
        print("No assets found.")
        return
    for key in sorted(assets):
        asset = assets[key]
        rel_path = asset.path.relative_to(project_root)
        print(f"- {asset.key} [{asset.kind}] ({rel_path})")
        if asset.description:
            print(f"  description: {asset.description}")
        for index, dependency in enumerate(asset.depends):
            connector = "└─" if index == len(asset.depends) - 1 else "├─"
            print(f"  {connector} {dependency}")


def _docs(args: argparse.Namespace) -> None:
    generate_docs(args.out, sample_rows=args.sample_rows)


def _status(_: argparse.Namespace) -> None:
    show_status()


def _prune(_: argparse.Namespace) -> None:
    prune_tables()


def _test(args: argparse.Namespace) -> None:
    test_assets(sample_rows=args.sample_rows)


def _publish(args: argparse.Namespace) -> None:
    publish(args.target, args.selectors)


def _show(args: argparse.Namespace) -> None:
    show_asset(args.asset, sample_rows=args.sample_rows)


def _query(args: argparse.Namespace) -> None:
    statement = args.statement.strip()
    if not statement:
        raise ValueError("SQL statement must not be empty.")

    with db_connection(read_only=True) as conn:
        conn.sql(statement).show()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fdp",
        description="Filecoin Data Portal CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    materialize_parser = subparsers.add_parser(
        "materialize",
        help="Refresh assets in DuckDB.",
        description=(
            "Refresh assets in DuckDB. Selectors can be exact asset keys like "
            "'raw.some_asset', asset folders like 'main' and 'main.daily', "
            "or asset file/folder paths like "
            "'assets/main/daily/storage_providers_metrics.sql'. With explicit "
            "selectors, refreshes only those assets by default. Use "
            "--with-deps to refresh transitive dependencies too. With no "
            "selectors, refreshes everything."
        ),
    )
    materialize_parser.add_argument(
        "selectors",
        nargs="*",
        metavar="SELECTOR",
        help=(
            "Asset keys, asset folders, or asset file/folder paths to "
            "refresh. Examples: 'main', 'main.daily', 'raw.some_asset', "
            "'assets/main/daily/storage_providers_metrics.sql'. Defaults to "
            "all assets."
        ),
    )
    materialize_parser.add_argument(
        "--with-deps",
        action="store_true",
        help=(
            "Refresh selected assets and their transitive dependencies. By "
            "default, explicit selectors refresh only the matched assets."
        ),
    )
    materialize_parser.set_defaults(func=_materialize)

    check_parser = subparsers.add_parser(
        "check",
        help="Validate assets.",
    )
    check_parser.set_defaults(func=_check)

    list_parser = subparsers.add_parser(
        "list",
        help="List available assets.",
    )
    list_parser.set_defaults(func=_list_assets)

    status_parser = subparsers.add_parser(
        "status",
        help="Compare asset files with materialized DuckDB tables.",
    )
    status_parser.set_defaults(func=_status)

    prune_parser = subparsers.add_parser(
        "prune",
        help="Drop materialized DuckDB tables with no matching asset file.",
    )
    prune_parser.set_defaults(func=_prune)

    docs_parser = subparsers.add_parser(
        "docs",
        help="Generate markdown docs for main tables and the FDP skill.",
    )
    docs_parser.add_argument(
        "--out",
        help="Output directory. Defaults to <project>/build/docs.",
    )
    docs_parser.add_argument(
        "--sample-rows",
        type=int,
        default=10,
        help="Number of sample rows per asset.",
    )
    docs_parser.set_defaults(func=_docs)

    test_parser = subparsers.add_parser(
        "test",
        help="Run data tests against already materialized assets.",
        description=(
            "Run inline and SQL data tests against already materialized assets."
        ),
    )
    test_parser.add_argument(
        "--sample-rows",
        type=int,
        default=10,
        help="Number of failing rows to print per failed test.",
    )
    test_parser.set_defaults(func=_test)

    publish_parser = subparsers.add_parser(
        "publish",
        help="Publish materialized main tables to a target.",
        description=(
            "Publish materialized main tables to a target. Selectors can be "
            "exact asset keys like 'main.some_asset', asset folders like "
            "'main' and 'main.daily', or asset file/folder paths like "
            "'assets/main/daily/storage_providers_metrics.sql'. With no "
            "selectors, publishes all main assets."
        ),
    )
    publish_parser.add_argument(
        "target",
        choices=available_targets(),
        help="Publish target.",
    )
    publish_parser.add_argument(
        "selectors",
        nargs="*",
        metavar="SELECTOR",
        help=(
            "Main asset keys, asset folders, or asset file/folder paths to "
            "publish. Examples: 'main', 'main.daily', "
            "'main.daily_storage_providers_metrics', "
            "'assets/main/daily/storage_providers_metrics.sql'. Defaults to "
            "all main assets."
        ),
    )
    publish_parser.set_defaults(func=_publish)

    show_parser = subparsers.add_parser(
        "show",
        help="Show details for an asset.",
    )
    show_parser.add_argument(
        "asset",
        metavar="SELECTOR",
        help="Asset key, folder, or file path to inspect.",
    )
    show_parser.add_argument(
        "--sample-rows",
        type=int,
        default=5,
        help="Number of sample rows to print when materialized.",
    )
    show_parser.set_defaults(func=_show)

    query_parser = subparsers.add_parser(
        "query",
        help="Run a read-only SQL query against DuckDB.",
        description=(
            "Run a read-only SQL query against DuckDB. "
            "Wrap the SQL statement in quotes."
        ),
    )
    query_parser.add_argument(
        "statement",
        metavar="SQL",
        help="SQL statement to execute.",
    )
    query_parser.set_defaults(func=_query)

    args = parser.parse_args()
    args.func(args)
