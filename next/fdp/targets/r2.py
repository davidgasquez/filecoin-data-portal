import os
from dataclasses import dataclass

import duckdb

from fdp.assets import Asset


@dataclass(frozen=True)
class R2Config:
    access_key_id: str
    secret_access_key: str
    account_id: str
    bucket: str


def publish(assets: list[Asset], conn: duckdb.DuckDBPyConnection) -> None:
    config = r2_config_from_env()
    install_httpfs(conn)
    create_temporary_r2_secret(conn, config)
    publish_assets(conn, assets, config.bucket)


def r2_config_from_env() -> R2Config:
    values = {
        "FDP_R2_ACCESS_KEY_ID": os.environ.get("FDP_R2_ACCESS_KEY_ID", ""),
        "FDP_R2_SECRET_ACCESS_KEY": os.environ.get("FDP_R2_SECRET_ACCESS_KEY", ""),
        "FDP_R2_ACCOUNT_ID": os.environ.get("FDP_R2_ACCOUNT_ID", ""),
        "FDP_R2_BUCKET": os.environ.get("FDP_R2_BUCKET", ""),
    }
    missing = [name for name, value in values.items() if not value]
    if missing:
        names = ", ".join(missing)
        raise ValueError(f"Missing R2 environment variables: {names}")

    return R2Config(
        access_key_id=values["FDP_R2_ACCESS_KEY_ID"],
        secret_access_key=values["FDP_R2_SECRET_ACCESS_KEY"],
        account_id=values["FDP_R2_ACCOUNT_ID"],
        bucket=values["FDP_R2_BUCKET"],
    )


def install_httpfs(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("install httpfs")
    conn.execute("load httpfs")


def create_temporary_r2_secret(
    conn: duckdb.DuckDBPyConnection,
    config: R2Config,
) -> None:
    conn.execute(
        "create or replace temporary secret fdp_publish_r2 ("
        "type r2, "
        "key_id ?, "
        "secret ?, "
        "account_id ?, "
        "scope ?"
        ")",
        [
            config.access_key_id,
            config.secret_access_key,
            config.account_id,
            r2_scope(config.bucket),
        ],
    )


def r2_scope(bucket: str) -> str:
    return f"r2://{bucket}/"


def publish_assets(
    conn: duckdb.DuckDBPyConnection,
    assets: list[Asset],
    bucket: str,
) -> None:
    total = len(assets)
    count_width = len(str(total))
    asset_width = max((len(asset.key) for asset in assets), default=0)

    for index, asset in enumerate(assets, start=1):
        filename, row_count, file_size_bytes = publish_asset(conn, asset, bucket)
        print(
            f"[{index:>{count_width}}/{total:>{count_width}}] "
            f"{asset.key:<{asset_width}} OK "
            f"rows={row_count} bytes={file_size_bytes} {filename}",
            flush=True,
        )


def publish_asset(
    conn: duckdb.DuckDBPyConnection,
    asset: Asset,
    bucket: str,
) -> tuple[str, int, int]:
    stats = conn.execute(
        f"copy (select * from {asset.key}) to ? ("
        "format parquet, "
        "compression zstd, "
        "compression_level 1, "
        "row_group_size 1000000, "
        "return_stats"
        ")",
        [r2_target_path(bucket, asset.name)],
    ).fetchone()
    if stats is None:
        raise RuntimeError(f"Publish returned no stats for {asset.key}")

    filename, row_count, file_size_bytes, *_ = stats
    return str(filename), int(row_count), int(file_size_bytes)


def r2_target_path(bucket: str, table: str) -> str:
    return f"r2://{bucket}/{table}.parquet"
