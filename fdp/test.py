from dataclasses import dataclass
from pathlib import Path

from fdp.api import db_connection
from fdp.assets import load_assets
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
    tests = data_tests(asset_views, loaded.project_root)
    if not tests:
        print("No data tests found.", flush=True)
        return

    run_data_tests(tests, sample_rows)


def data_tests(asset_views: list[AssetView], project_root: Path) -> list[DataTest]:
    tests: list[DataTest] = []
    for asset_view in asset_views:
        asset = asset_view.asset
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

    for asset_view in asset_views:
        for custom_test in asset_view.custom_tests:
            query = custom_test.path.read_text(encoding="utf-8").strip()
            if not query:
                raise ValueError(f"Data test file is empty: {custom_test.path}")
            tests.append(
                DataTest(
                    name=f"{asset_view.asset.key}__{custom_test.name}",
                    query=query.removesuffix(";").rstrip(),
                    source=custom_test.path.relative_to(project_root).as_posix(),
                )
            )
    return tests


def run_data_tests(tests: list[DataTest], sample_rows: int) -> None:
    total = len(tests)
    count_width = len(str(total))
    name_width = max((len(test.name) for test in tests), default=0)
    failed_tests: list[str] = []

    with db_connection(read_only=True) as conn:
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
