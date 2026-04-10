from dataclasses import dataclass
from pathlib import Path

import duckdb

from fdp.api import db_connection, ensure_tables_exist, find_assets_root
from fdp.assets import (
    Asset,
    ordered_assets,
    validate_asset_reference,
    validate_identifier,
)


@dataclass(frozen=True)
class DataTest:
    name: str
    query: str
    source: str


def format_cell(value: object, *, lowercase_bools: bool = False) -> str:
    if value is None:
        return "null"
    if lowercase_bools and isinstance(value, bool):
        return str(value).lower()
    return str(value)


def render_text_table(
    columns: list[str],
    rows: list[tuple[object, ...]],
    *,
    lowercase_bools: bool = False,
) -> list[str]:
    if not columns:
        return ["no columns"]
    if not rows:
        return ["no rows"]

    rendered_rows = [
        [format_cell(value, lowercase_bools=lowercase_bools) for value in row]
        for row in rows
    ]
    widths = [len(column) for column in columns]
    for row in rendered_rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    header = " | ".join(
        column.ljust(widths[index]) for index, column in enumerate(columns)
    )
    divider = "-+-".join("-" * width for width in widths)
    body = [
        " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rendered_rows
    ]
    return [header, divider, *body]


def test_assets(sample_rows: int = 10) -> None:
    if sample_rows < 1:
        raise ValueError("sample_rows must be at least 1")

    assets = ordered_assets()
    with db_connection(read_only=True) as conn:
        ensure_tables_exist(conn, assets)
        validate_column_metadata(conn, assets)

    tests = collect_data_tests(assets)
    if not tests:
        print("No data tests found.", flush=True)
        return

    run_data_tests(tests, sample_rows)


def validate_column_metadata(
    conn: duckdb.DuckDBPyConnection,
    assets: list[Asset],
) -> None:
    for asset in assets:
        validate_asset_columns(conn, asset)


def validate_asset_columns(conn: duckdb.DuckDBPyConnection, asset: Asset) -> None:
    actual_columns = {
        column_name
        for column_name, _ in conn.execute(
            "select column_name, data_type "
            "from information_schema.columns "
            "where table_schema = ? and table_name = ? "
            "order by ordinal_position",
            [asset.schema, asset.name],
        ).fetchall()
    }
    for column in asset.columns:
        if column.name in actual_columns:
            continue
        raise ValueError(
            f"Asset {asset.key} metadata references missing column "
            f"'{column.name}'. Run `uv run --env-file .env fdp materialize` "
            "after fixing the asset."
        )


def collect_data_tests(assets: list[Asset]) -> list[DataTest]:
    assets_root = find_assets_root()
    project_root = assets_root.parent
    indexed_assets = {asset.key: asset for asset in assets}
    return [
        *inline_data_tests(assets, project_root),
        *custom_sql_tests(assets_root, project_root, indexed_assets),
    ]


def inline_data_tests(assets: list[Asset], project_root: Path) -> list[DataTest]:
    tests: list[DataTest] = []
    for asset in assets:
        source = f"metadata:{asset.path.relative_to(project_root).as_posix()}"
        if asset.tests.not_null:
            tests.append(
                DataTest(
                    name=f"{asset.key}__not_null",
                    query=not_null_query(asset),
                    source=source,
                )
            )

        for column in asset.tests.unique:
            tests.append(
                DataTest(
                    name=f"{asset.key}__unique_{column}",
                    query=unique_query(asset, column),
                    source=source,
                )
            )

        for index, assertion in enumerate(asset.tests.assertions, start=1):
            tests.append(
                DataTest(
                    name=f"{asset.key}__assert_{index}",
                    query=assertion_query(asset, assertion),
                    source=source,
                )
            )
    return tests


def custom_sql_tests(
    assets_root: Path,
    project_root: Path,
    assets: dict[str, Asset],
) -> list[DataTest]:
    return [
        sql_data_test_from_path(path, assets_root, project_root, assets)
        for path in custom_test_paths(assets_root)
    ]


def sql_data_test_from_path(
    path: Path,
    assets_root: Path,
    project_root: Path,
    assets: dict[str, Asset],
) -> DataTest:
    asset_key, test_name = data_test_identity_from_path(path, assets_root)
    if asset_key not in assets:
        raise ValueError(f"Unknown asset '{asset_key}' referenced in {path}")

    return DataTest(
        name=f"{asset_key}__{test_name}",
        query=read_test_query(path),
        source=path.relative_to(project_root).as_posix(),
    )


def not_null_query(asset: Asset) -> str:
    conditions = " or ".join(f"{column} is null" for column in asset.tests.not_null)
    return f"select * from {asset.key} where {conditions}"


def unique_query(asset: Asset, column: str) -> str:
    return (
        f"select {column}, count(*) as n "
        f"from {asset.key} "
        f"group by {column} "
        "having count(*) > 1"
    )


def assertion_query(asset: Asset, assertion: str) -> str:
    return f"select * from {asset.key} where not ({assertion})"


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


def asset_test_lines(asset: Asset, assets_root: Path, project_root: Path) -> list[str]:
    lines = [
        *(f"not_null: {column}" for column in asset.tests.not_null),
        *(f"unique: {column}" for column in asset.tests.unique),
        *(f"assert: {assertion}" for assertion in asset.tests.assertions),
    ]
    for path in custom_test_paths_for_asset(asset, assets_root):
        lines.append(f"custom: {path.relative_to(project_root).as_posix()}")
    return lines


def custom_test_paths(assets_root: Path) -> list[Path]:
    return sorted(assets_root.rglob("*.test.sql"))


def custom_test_paths_for_asset(asset: Asset, assets_root: Path) -> list[Path]:
    return [
        path
        for path in custom_test_paths(assets_root)
        if data_test_identity_from_path(path, assets_root)[0] == asset.key
    ]


def data_test_identity_from_path(path: Path, assets_root: Path) -> tuple[str, str]:
    relative_path = path.relative_to(assets_root)
    if len(relative_path.parts) < 2:
        raise ValueError(
            f"Data test path must include a schema folder under assets: {path}"
        )

    schema = relative_path.parts[0]
    validate_identifier(schema, "schema", path)
    asset_name, separator, test_name = path.name.removesuffix(".test.sql").partition(
        "__"
    )
    if not separator or not test_name:
        raise ValueError(
            f"Invalid data test file name '{path}'. Expected asset__name.test.sql"
        )

    validate_identifier(asset_name, "table", path)
    validate_identifier(test_name, "test", path)
    asset_key = f"{schema}.{asset_name}"
    validate_asset_reference(asset_key, path)
    return asset_key, test_name


def read_test_query(path: Path) -> str:
    query = path.read_text(encoding="utf-8").strip()
    if not query:
        raise ValueError(f"Data test file is empty: {path}")
    if query.endswith(";"):
        return query[:-1].rstrip()
    return query
