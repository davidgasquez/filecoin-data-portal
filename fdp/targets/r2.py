import json
import os
import subprocess
from dataclasses import dataclass

import duckdb
import httpx

from fdp.assets import Asset, main_assets

ENV_VARS = {
    "access_key_id": "R2_ACCESS_KEY_ID",
    "secret_access_key": "R2_SECRET_ACCESS_KEY",
    "account_id": "R2_ACCOUNT_ID",
    "bucket": "R2_BUCKET",
    "cloudflare_api_token": "CLOUDFLARE_API_TOKEN",
    "cloudflare_zone_id": "CLOUDFLARE_ZONE_ID",
}


@dataclass(frozen=True)
class R2Config:
    access_key_id: str
    secret_access_key: str
    account_id: str
    bucket: str
    cloudflare_api_token: str
    cloudflare_zone_id: str


def publish(assets: list[Asset], conn: duckdb.DuckDBPyConnection) -> None:
    config = r2_config_from_env()
    conn.execute("install httpfs")
    conn.execute("load httpfs")
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
            f"r2://{config.bucket}/",
        ],
    )
    publish_assets(conn, assets, config.bucket)
    if {asset.key for asset in assets} == {asset.key for asset in main_assets()}:
        prune_exports(config, {f"{asset.name}.parquet" for asset in assets})
    purge_cache(config)


def r2_config_from_env() -> R2Config:
    missing = [v for v in ENV_VARS.values() if not os.environ.get(v)]
    if missing:
        raise ValueError(
            f"Missing R2 publishing environment variables: {', '.join(missing)}"
        )
    return R2Config(**{f: os.environ[v] for f, v in ENV_VARS.items()})


def prune_exports(config: R2Config, keep: set[str]) -> None:
    output = aws(
        config,
        "s3api",
        "list-objects-v2",
        "--bucket",
        config.bucket,
        "--delimiter",
        "/",
        "--query",
        "Contents[].Key",
    )
    stale = [
        key
        for key in json.loads(output) or []
        if key.endswith(".parquet") and key not in keep
    ]
    for key in sorted(stale):
        aws(config, "s3", "rm", f"s3://{config.bucket}/{key}")
        print(f"Pruned stale export {key}", flush=True)


def aws(config: R2Config, *args: str) -> str:
    return subprocess.run(
        [
            "aws",
            *args,
            "--output",
            "json",
            "--region",
            "auto",
            "--endpoint-url",
            f"https://{config.account_id}.r2.cloudflarestorage.com",
        ],
        env=os.environ
        | {
            "AWS_ACCESS_KEY_ID": config.access_key_id,
            "AWS_SECRET_ACCESS_KEY": config.secret_access_key,
        },
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout


def purge_cache(config: R2Config) -> None:
    response = httpx.post(
        "https://api.cloudflare.com/client/v4/zones/"
        f"{config.cloudflare_zone_id}/purge_cache",
        headers={"Authorization": f"Bearer {config.cloudflare_api_token}"},
        json={"hosts": ["data.filecoindataportal.xyz"]},
        timeout=30,
    )
    response.raise_for_status()
    result = response.json()
    if not result["success"]:
        raise RuntimeError(f"Cloudflare cache purge failed: {result['errors']}")
    print("Purged data.filecoindataportal.xyz cache", flush=True)


def publish_assets(
    conn: duckdb.DuckDBPyConnection,
    assets: list[Asset],
    bucket: str,
) -> None:
    total = len(assets)
    count_width = len(str(total))
    asset_width = max(len(asset.key) for asset in assets)

    for index, asset in enumerate(assets, start=1):
        filename, row_count, file_size_bytes, *_ = conn.execute(
            f"copy (select * from {asset.key}) to ? ("
            "format parquet, "
            "compression zstd, "
            "compression_level 1, "
            "row_group_size 1000000, "
            "return_stats"
            ")",
            [f"r2://{bucket}/{asset.name}.parquet"],
        ).fetchall()[0]
        if asset.key == "main.daily_network_metrics":
            conn.execute(
                f"copy (select * from {asset.key}) to ? (format json, array true)",
                [f"r2://{bucket}/{asset.name}.json"],
            )
        print(
            f"[{index:>{count_width}}/{total:>{count_width}}] "
            f"{asset.key:<{asset_width}} OK "
            f"rows={row_count} bytes={file_size_bytes} {filename}",
            flush=True,
        )
