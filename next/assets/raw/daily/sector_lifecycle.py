# ruff: noqa: E501
# asset.description = Daily Filecoin sector lifecycle bytes from Lily miner sector events. Before 2026-01-16, terminated metrics include expirations because Lily did not emit SECTOR_EXPIRED yet.
# asset.materialization = custom
# asset.column = date | UTC day for the sector lifecycle metrics.
# asset.column = onboarded_bytes | Total raw sector bytes onboarded on the day from SECTOR_ADDED and COMMIT_CAPACITY_ADDED.
# asset.column = onboarded_sectors | Total sectors onboarded on the day.
# asset.column = terminated_bytes | Total raw sector bytes terminated on the day from SECTOR_TERMINATED. Before 2026-01-16 this also includes expirations.
# asset.column = terminated_sectors | Total sectors terminated on the day. Before 2026-01-16 this also includes expirations.
# asset.column = expired_bytes | Total raw sector bytes expired on the day from SECTOR_EXPIRED.
# asset.column = expired_sectors | Total sectors expired on the day from SECTOR_EXPIRED.
# asset.column = removed_bytes | Total raw sector bytes removed on the day from termination or expiration.
# asset.column = removed_sectors | Total sectors removed on the day from termination or expiration.
# asset.not_null = date
# asset.not_null = onboarded_bytes
# asset.not_null = onboarded_sectors
# asset.not_null = terminated_bytes
# asset.not_null = terminated_sectors
# asset.not_null = expired_bytes
# asset.not_null = expired_sectors
# asset.not_null = removed_bytes
# asset.not_null = removed_sectors
# asset.unique = date
# asset.assert = onboarded_bytes >= 0
# asset.assert = onboarded_sectors >= 0
# asset.assert = terminated_bytes >= 0
# asset.assert = terminated_sectors >= 0
# asset.assert = expired_bytes >= 0
# asset.assert = expired_sectors >= 0
# asset.assert = removed_bytes >= 0
# asset.assert = removed_sectors >= 0

import os

from google.cloud import bigquery

from fdp.api import db_connection
from fdp.google import credentials_from_env

ASSET_KEY = "raw.daily_sector_lifecycle"
SCHEMA = "raw"
DEFAULT_PROJECT = "protocol-labs-data-nexus"
DEFAULT_LOCATION = "us-east4"
QUERY = """
with miner_sizes as (
    select
        miner_id,
        max(cast(sector_size as int64)) as sector_size
    from `lily-data.lily.miner_infos`
    where cast(sector_size as int64) > 0
    group by 1
)
select
    date(timestamp_seconds((e.height * 30) + 1598306400)) as date,
    sum(case when e.event in ('SECTOR_ADDED', 'COMMIT_CAPACITY_ADDED') then ms.sector_size else 0 end) as onboarded_bytes,
    countif(e.event in ('SECTOR_ADDED', 'COMMIT_CAPACITY_ADDED')) as onboarded_sectors,
    sum(case when e.event = 'SECTOR_TERMINATED' then ms.sector_size else 0 end) as terminated_bytes,
    countif(e.event = 'SECTOR_TERMINATED') as terminated_sectors,
    sum(case when e.event = 'SECTOR_EXPIRED' then ms.sector_size else 0 end) as expired_bytes,
    countif(e.event = 'SECTOR_EXPIRED') as expired_sectors,
    sum(case when e.event in ('SECTOR_TERMINATED', 'SECTOR_EXPIRED') then ms.sector_size else 0 end) as removed_bytes,
    countif(e.event in ('SECTOR_TERMINATED', 'SECTOR_EXPIRED')) as removed_sectors
from `lily-data.lily.miner_sector_events` as e
join miner_sizes as ms
    using (miner_id)
where e.event in (
    'SECTOR_ADDED',
    'COMMIT_CAPACITY_ADDED',
    'SECTOR_TERMINATED',
    'SECTOR_EXPIRED'
)
group by 1
order by 1
""".strip()


def materialize_bigquery_asset() -> None:
    client = bigquery.Client(
        project=os.environ.get("FDP_BIGQUERY_PROJECT", DEFAULT_PROJECT),
        location=os.environ.get("FDP_BIGQUERY_LOCATION", DEFAULT_LOCATION),
        credentials=credentials_from_env(),
    )
    job_config = bigquery.QueryJobConfig(
        priority=bigquery.QueryPriority.BATCH,
        allow_large_results=True,
    )
    arrow_table = client.query(QUERY, job_config=job_config).to_arrow(
        create_bqstorage_client=True
    )
    with db_connection() as conn:
        conn.execute(f"create schema if not exists {SCHEMA}")
        conn.register("bigquery_result", arrow_table)
        conn.execute(
            f"create or replace table {ASSET_KEY} as select * from bigquery_result"
        )


def sector_lifecycle() -> None:
    materialize_bigquery_asset()
