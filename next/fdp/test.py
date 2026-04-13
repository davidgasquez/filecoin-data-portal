from dataclasses import dataclass
from pathlib import Path

import duckdb

from fdp.api import db_connection
from fdp.assets import load_assets, read_custom_sql_test_query
from fdp.inspect import AssetView, inspect_assets
from fdp.tabular import render_text_table


@dataclass(frozen=True)
class DataTest:
    name: str
    query: str
    source: str


def test_assets(sample_rows: int = 10) -> None:
    if sample_rows < 1:
        raise ValueError("sample_rows must be at least 1")

    loaded = load_assets()
    asset_views = inspect_assets(loaded, require_materialized=True)
    tests = collect_data_tests(asset_views, loaded.root.parent)
    if not tests:
        print("No data tests found.", flush=True)
        return

    run_data_tests(tests, sample_rows)


def collect_data_tests(
    asset_views: list[AssetView],
    project_root: Path,
) -> list[DataTest]:
    return [
        *inline_data_tests(asset_views, project_root),
        *custom_sql_tests(asset_views, project_root),
    ]


def inline_data_tests(
    asset_views: list[AssetView],
    project_root: Path,
) -> list[DataTest]:
    tests: list[DataTest] = []
    for asset_view in asset_views:
        asset = asset_view.asset
        source = f"metadata:{asset.path.relative_to(project_root).as_posix()}"
        if asset.tests.not_null:
            tests.append(
                DataTest(
                    name=f"{asset.key}__not_null",
                    query=not_null_query(asset_view),
                    source=source,
                )
            )

        for column in asset.tests.unique:
            tests.append(
                DataTest(
                    name=f"{asset.key}__unique_{column}",
                    query=unique_query(asset_view, column),
                    source=source,
                )
            )

        for index, assertion in enumerate(asset.tests.assertions, start=1):
            tests.append(
                DataTest(
                    name=f"{asset.key}__assert_{index}",
                    query=assertion_query(asset_view, assertion),
                    source=source,
                )
            )
    return tests


def custom_sql_tests(
    asset_views: list[AssetView],
    project_root: Path,
) -> list[DataTest]:
    tests: list[DataTest] = []
    for asset_view in asset_views:
        asset = asset_view.asset
        for custom_test in asset_view.custom_tests:
            tests.append(
                DataTest(
                    name=f"{asset.key}__{custom_test.name}",
                    query=read_custom_sql_test_query(custom_test.path),
                    source=custom_test.path.relative_to(project_root).as_posix(),
                )
            )
    return tests


def not_null_query(asset_view: AssetView) -> str:
    asset = asset_view.asset
    conditions = " or ".join(f"{column} is null" for column in asset.tests.not_null)
    return f"select * from {asset.key} where {conditions}"


def unique_query(asset_view: AssetView, column: str) -> str:
    asset = asset_view.asset
    return (
        f"select {column}, count(*) as n "
        f"from {asset.key} "
        f"group by {column} "
        "having count(*) > 1"
    )


def assertion_query(asset_view: AssetView, assertion: str) -> str:
    return f"select * from {asset_view.asset.key} where not ({assertion})"


def run_data_tests(tests: list[DataTest], sample_rows: int) -> None:
    total = len(tests)
    count_width = len(str(total))
    name_width = max((len(test.name) for test in tests), default=0)
    failed_tests: list[str] = []

    with db_connection(read_only=True) as conn:
        for index, test in enumerate(tests, start=1):
            failing_rows = count_failing_rows(conn, test.query)
            status = "FAIL" if failing_rows else "OK"
            print(
                f"[{index:>{count_width}}/{total:>{count_width}}] "
                f"{test.name:<{name_width}} {status}",
                flush=True,
            )
            if not failing_rows:
                continue

            failed_tests.append(test.name)
            print(f"  source: {test.source}", flush=True)
            print(f"  failing rows: {failing_rows}", flush=True)
            cursor = conn.execute(
                f"select * from ({test.query}) as failing_rows limit {sample_rows}"
            )
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            print("  sample:", flush=True)
            for line in render_text_table(columns, rows):
                print(f"  {line}", flush=True)

    if failed_tests:
        raise ValueError(f"{len(failed_tests)} data tests failed")


def count_failing_rows(conn: duckdb.DuckDBPyConnection, query: str) -> int:
    row = conn.execute(f"select count(*) from ({query}) as counted_rows").fetchone()
    if row is None:
        raise ValueError("Missing row count")
    return int(row[0])
