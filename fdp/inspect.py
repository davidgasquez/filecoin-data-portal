from collections.abc import Iterable
from dataclasses import dataclass

import duckdb

from fdp.api import db_connection, table_exists
from fdp.assets import Asset


@dataclass(frozen=True)
class MaterializedColumn:
    name: str
    data_type: str


@dataclass(frozen=True)
class AssetView:
    asset: Asset
    exists: bool
    columns: tuple[MaterializedColumn, ...]
    row_count: int | None
    sample_columns: tuple[str, ...]
    sample_rows: tuple[tuple[object, ...], ...]


def inspect_asset(asset: Asset, sample_rows: int) -> AssetView:
    with db_connection(read_only=True) as conn:
        if not table_exists(conn, asset.schema, asset.name):
            return AssetView(asset, False, (), None, (), ())

        columns = validate_materialized_asset(conn, asset)
        cursor = conn.execute(f"select * from {asset.key} limit {sample_rows}")
        rows = tuple(cursor.fetchall())
        sample_columns = tuple(description[0] for description in cursor.description)
        row_count = conn.execute(f"select count(*) from {asset.key}").fetchone()
        if row_count is None:
            raise ValueError(f"Missing row count for {asset.key}")
        return AssetView(asset, True, columns, int(row_count[0]), sample_columns, rows)


def validate_materialized_asset(
    conn: duckdb.DuckDBPyConnection,
    asset: Asset,
) -> tuple[MaterializedColumn, ...]:
    columns = materialized_columns(conn, asset)
    actual = {column.name for column in columns}

    if asset.columns:
        documented = {column.name for column in asset.columns}
        missing_columns = sorted(documented - actual)
        extra_columns = sorted(actual - documented)
        if missing_columns or extra_columns:
            raise ValueError(
                f"Asset {asset.key} documented columns do not match "
                "materialized columns. "
                f"Run `uv run --env-file .env fdp materialize {asset.key}` "
                "after fixing the asset. "
                f"missing={missing_columns} extra={extra_columns}"
            )

    for name in (*asset.tests.not_null, *asset.tests.unique):
        if name not in actual:
            raise ValueError(
                f"Asset {asset.key} test references missing column '{name}'"
            )

    return columns


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
    return tuple(MaterializedColumn(*row) for row in rows)


def ensure_tables_exist(
    conn: duckdb.DuckDBPyConnection,
    assets: Iterable[Asset],
) -> None:
    missing_assets = [
        asset.key
        for asset in assets
        if not table_exists(conn, asset.schema, asset.name)
    ]
    if missing_assets:
        missing = ", ".join(missing_assets)
        raise ValueError(
            "Assets are not materialized: "
            f"{missing}. Run `uv run --env-file .env fdp materialize` first."
        )
