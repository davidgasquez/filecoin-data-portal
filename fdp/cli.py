import argparse

from fdp.api import db_connection
from fdp.assets import check_assets, load_assets
from fdp.export import export
from fdp.materialize import materialize
from fdp.publish import TARGETS, publish
from fdp.show import show_asset
from fdp.status import prune_tables, show_status
from fdp.test import test_assets


def list_assets() -> None:
    loaded = load_assets()
    assets = loaded.assets
    if not assets:
        print("No assets found.")
        return
    for key in sorted(assets):
        asset = assets[key]
        rel_path = asset.path.relative_to(loaded.project_root)
        print(f"- {asset.key} [{asset.kind}] ({rel_path})")
        if asset.description:
            print(f"  description: {asset.description}")
        for index, dependency in enumerate(asset.depends):
            connector = "└─" if index == len(asset.depends) - 1 else "├─"
            print(f"  {connector} {dependency}")


def query(statement: str) -> None:
    statement = statement.strip()
    if not statement:
        raise ValueError("SQL statement must not be empty.")

    with db_connection(read_only=True) as conn:
        result = conn.sql(statement)
        if result is not None:
            result.show()


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
            "'raw.riba_eth_logs', asset folders like 'main' and 'model.foc', "
            "or asset file/folder paths like "
            "'assets/main/daily_miner_metrics.sql'. With explicit "
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
            "refresh. Examples: 'main', 'model.foc', 'raw.riba_eth_logs', "
            "'assets/main/daily_miner_metrics.sql'. Defaults to "
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

    subparsers.add_parser("check", help="Validate assets.")
    subparsers.add_parser("list", help="List available assets.")
    subparsers.add_parser(
        "status", help="Compare asset files with materialized DuckDB tables."
    )
    subparsers.add_parser(
        "prune", help="Drop materialized DuckDB tables with no matching asset file."
    )

    export_parser = subparsers.add_parser(
        "export",
        help="Export main tables to a standalone DuckDB file.",
    )
    export_parser.add_argument(
        "--out",
        help="Output DuckDB path. Defaults to <project>/build/fdp.duckdb.",
    )

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

    publish_parser = subparsers.add_parser(
        "publish",
        help="Publish materialized main tables to a target.",
        description=(
            "Publish materialized main tables to a target. Selectors can be "
            "exact asset keys like 'main.providers', the 'main' folder, "
            "or asset file paths like "
            "'assets/main/daily_miner_metrics.sql'. With no "
            "selectors, publishes all main assets."
        ),
    )
    publish_parser.add_argument(
        "target",
        choices=sorted(TARGETS),
        help="Publish target.",
    )
    publish_parser.add_argument(
        "selectors",
        nargs="*",
        metavar="SELECTOR",
        help=(
            "Main asset keys, asset folders, or asset file/folder paths to "
            "publish. Examples: 'main', "
            "'main.daily_miner_metrics', "
            "'assets/main/daily_miner_metrics.sql'. Defaults to "
            "all main assets."
        ),
    )

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

    args = parser.parse_args()
    match args.command:
        case "materialize":
            materialize(args.selectors, include_dependencies=args.with_deps)
        case "check":
            check_assets()
        case "list":
            list_assets()
        case "status":
            show_status()
        case "prune":
            prune_tables()
        case "export":
            print(export(args.out))
        case "test":
            test_assets(sample_rows=args.sample_rows)
        case "publish":
            publish(args.target, args.selectors)
        case "show":
            show_asset(args.asset, sample_rows=args.sample_rows)
        case "query":
            query(args.statement)
