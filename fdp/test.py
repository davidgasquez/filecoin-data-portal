from dataclasses import dataclass

import duckdb

from fdp.api import db_connection
from fdp.assets import Asset, LoadedAssets, load_assets
from fdp.inspect import ensure_tables_exist, validate_materialized_asset
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
    assets = [loaded.assets[key] for key in loaded.ordered_keys]
    with db_connection(read_only=True) as conn:
        ensure_tables_exist(conn, assets)
        for asset in assets:
            validate_materialized_asset(conn, asset)
        tests = data_tests(loaded, assets)
        if not tests:
            print("No data tests found.", flush=True)
            return

        run_data_tests(conn, tests, sample_rows)


def data_tests(loaded: LoadedAssets, assets: list[Asset]) -> list[DataTest]:
    project_root = loaded.project_root
    tests: list[DataTest] = []
    for asset in assets:
        source = f"metadata:{asset.path.relative_to(project_root).as_posix()}"
        if asset.tests.not_null:
            conditions = " or ".join(
                f"{column} is null" for column in asset.tests.not_null
            )
            tests.append(
                DataTest(
                    name=f"{asset.key}__not_null",
                    query=f"select * from {asset.key} where {conditions}",
                    source=source,
                )
            )

        for column in asset.tests.unique:
            tests.append(
                DataTest(
                    name=f"{asset.key}__unique_{column}",
                    query=(
                        f"select {column}, count(*) as n "
                        f"from {asset.key} "
                        f"group by {column} "
                        "having count(*) > 1"
                    ),
                    source=source,
                )
            )

        for index, assertion in enumerate(asset.tests.assertions, start=1):
            tests.append(
                DataTest(
                    name=f"{asset.key}__assert_{index}",
                    query=f"select * from {asset.key} where not ({assertion})",
                    source=source,
                )
            )

    for asset in assets:
        for custom_test in loaded.custom_tests_by_asset[asset.key]:
            query = custom_test.path.read_text(encoding="utf-8").strip()
            if not query:
                raise ValueError(f"Data test file is empty: {custom_test.path}")
            tests.append(
                DataTest(
                    name=f"{asset.key}__{custom_test.name}",
                    query=query.removesuffix(";").rstrip(),
                    source=custom_test.path.relative_to(project_root).as_posix(),
                )
            )
    return tests


def run_data_tests(
    conn: duckdb.DuckDBPyConnection, tests: list[DataTest], sample_rows: int
) -> None:
    total = len(tests)
    count_width = len(str(total))
    name_width = max(len(test.name) for test in tests)
    failed = 0

    for index, test in enumerate(tests, start=1):
        failing_rows = conn.execute(
            f"select count(*) from ({test.query}) as counted_rows"
        ).fetchall()[0][0]
        status = "FAIL" if failing_rows else "OK"
        print(
            f"[{index:>{count_width}}/{total:>{count_width}}] "
            f"{test.name:<{name_width}} {status}",
            flush=True,
        )
        if not failing_rows:
            continue

        failed += 1
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

    if failed:
        raise ValueError(f"{failed} data tests failed")
