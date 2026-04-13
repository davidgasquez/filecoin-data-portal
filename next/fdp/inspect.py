from collections.abc import Iterable
from dataclasses import dataclass

import duckdb

from fdp.api import db_connection, ensure_tables_exist, table_exists
from fdp.assets import Asset, CustomSqlTest, LoadedAssets


@dataclass(frozen=True)
class MaterializedColumn:
    name: str
    data_type: str


@dataclass(frozen=True)
class AssetView:
    asset: Asset
    custom_tests: tuple[CustomSqlTest, ...]
    exists: bool
    columns: tuple[MaterializedColumn, ...]
    row_count: int | None
    sample_columns: tuple[str, ...]
    sample_rows: tuple[tuple[object, ...], ...]


def inspect_assets(
    loaded: LoadedAssets,
    *,
    asset_keys: Iterable[str] | None = None,
    require_materialized: bool = False,
    include_row_count: bool = False,
    sample_rows: int = 0,
) -> list[AssetView]:
    if sample_rows < 0:
        raise ValueError("sample_rows must be at least 0")

    selected_keys = selected_asset_keys(loaded, asset_keys)
    selected_assets = [loaded.assets[key] for key in selected_keys]
    with db_connection(read_only=True) as conn:
        if require_materialized:
            ensure_tables_exist(conn, selected_assets)
        return [
            inspect_asset(
                conn,
                loaded.assets[key],
                loaded.custom_tests_by_asset[key],
                include_row_count=include_row_count,
                sample_rows=sample_rows,
            )
            for key in selected_keys
        ]


def selected_asset_keys(
    loaded: LoadedAssets,
    asset_keys: Iterable[str] | None,
) -> tuple[str, ...]:
    if asset_keys is None:
        return loaded.ordered_keys

    selected: list[str] = []
    seen: set[str] = set()
    for key in asset_keys:
        if key not in loaded.assets:
            raise ValueError(f"Unknown asset: {key}")
        if key in seen:
            continue
        seen.add(key)
        selected.append(key)
    return tuple(selected)


def inspect_asset(
    conn: duckdb.DuckDBPyConnection,
    asset: Asset,
    custom_tests: tuple[CustomSqlTest, ...],
    *,
    include_row_count: bool,
    sample_rows: int,
) -> AssetView:
    if not table_exists(conn, asset.schema, asset.name):
        return AssetView(
            asset=asset,
            custom_tests=custom_tests,
            exists=False,
            columns=(),
            row_count=None,
            sample_columns=(),
            sample_rows=(),
        )

    columns = validate_materialized_asset(conn, asset)
    row_count = materialized_row_count(conn, asset) if include_row_count else None
    sample_columns, rows = materialized_sample(conn, asset, sample_rows)
    return AssetView(
        asset=asset,
        custom_tests=custom_tests,
        exists=True,
        columns=columns,
        row_count=row_count,
        sample_columns=sample_columns,
        sample_rows=rows,
    )


def validate_materialized_asset(
    conn: duckdb.DuckDBPyConnection,
    asset: Asset,
) -> tuple[MaterializedColumn, ...]:
    columns = materialized_columns(conn, asset)
    actual_column_names = [column.name for column in columns]
    actual_column_set = set(actual_column_names)

    if asset.columns:
        validate_documented_columns(asset, actual_column_set)

    for column_name in [*asset.tests.not_null, *asset.tests.unique]:
        if column_name in actual_column_set:
            continue
        raise ValueError(
            f"Asset {asset.key} test references missing column '{column_name}'"
        )

    return columns


def validate_documented_columns(asset: Asset, actual_column_set: set[str]) -> None:
    documented_column_names = [column.name for column in asset.columns]
    documented_column_set = set(documented_column_names)
    missing_columns = sorted(documented_column_set - actual_column_set)
    extra_columns = sorted(actual_column_set - documented_column_set)
    if not missing_columns and not extra_columns:
        return

    raise ValueError(
        f"Asset {asset.key} documented columns do not match materialized columns. "
        f"Run `uv run --env-file .env fdp materialize {asset.key}` after fixing "
        f"the asset. missing={missing_columns} extra={extra_columns}"
    )


def materialized_columns(
    conn: duckdb.DuckDBPyConnection,
    asset: Asset,
) -> tuple[MaterializedColumn, ...]:
    rows = conn.execute(
        "select column_name, data_type "
        "from information_schema.columns "
        "where table_schema = ? and table_name = ? "
        "order by ordinal_position",
        [asset.schema, asset.name],
    ).fetchall()
    return tuple(
        MaterializedColumn(name=column_name, data_type=data_type)
        for column_name, data_type in rows
    )


def materialized_row_count(
    conn: duckdb.DuckDBPyConnection,
    asset: Asset,
) -> int:
    row = conn.execute(f"select count(*) from {asset.key}").fetchone()
    if row is None:
        raise ValueError(f"Missing row count for {asset.key}")
    return int(row[0])


def materialized_sample(
    conn: duckdb.DuckDBPyConnection,
    asset: Asset,
    sample_rows: int,
) -> tuple[tuple[str, ...], tuple[tuple[object, ...], ...]]:
    if sample_rows == 0:
        return (), ()

    cursor = conn.execute(f"select * from {asset.key} limit {sample_rows}")
    rows = tuple(cursor.fetchall())
    columns = tuple(description[0] for description in cursor.description)
    return columns, rows
