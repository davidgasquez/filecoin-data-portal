from collections.abc import Iterable

import duckdb

from fdp.api import table_exists
from fdp.assets import Asset


def validate_materialized_asset(
    conn: duckdb.DuckDBPyConnection,
    asset: Asset,
) -> list[tuple[str, str]]:
    columns = conn.execute(
        "select column_name, data_type "
        "from information_schema.columns "
        "where table_schema = ? and table_name = ? "
        "order by ordinal_position",
        [asset.schema, asset.name],
    ).fetchall()
    actual = {name for name, _ in columns}

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
