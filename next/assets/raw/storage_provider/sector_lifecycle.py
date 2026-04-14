# asset.description = Daily Filecoin sector lifecycle metrics by storage
# provider from Lily miner sector events. Before 2026-01-16, terminated
# metrics include expirations because Lily did not emit SECTOR_EXPIRED yet.

# asset.materialization = custom

# asset.column = date | UTC day for the sector lifecycle metrics.
# asset.column = provider_id | Filecoin storage provider miner actor id
# address.
# asset.column = onboarded_tibs | Total raw sector data onboarded by the
# provider on the day from SECTOR_ADDED and COMMIT_CAPACITY_ADDED, in
# tebibytes.
# asset.column = onboarded_sectors | Total sectors onboarded by the provider on
# the day.
# asset.column = terminated_tibs | Total raw sector data terminated by the
# provider on the day from SECTOR_TERMINATED, in tebibytes. Before 2026-01-16
# this also includes expirations.
# asset.column = terminated_sectors | Total sectors terminated by the provider
# on the day. Before 2026-01-16 this also includes expirations.
# asset.column = expired_tibs | Total raw sector data expired by the provider
# on the day from SECTOR_EXPIRED, in tebibytes.
# asset.column = expired_sectors | Total sectors expired by the provider on the
# day from SECTOR_EXPIRED.
# asset.column = removed_tibs | Total raw sector data removed by the provider
# on the day from termination or expiration, in tebibytes.
# asset.column = removed_sectors | Total sectors removed by the provider on the
# day from termination or expiration.

# asset.not_null = date
# asset.not_null = provider_id
# asset.not_null = onboarded_tibs
# asset.not_null = onboarded_sectors
# asset.not_null = terminated_tibs
# asset.not_null = terminated_sectors
# asset.not_null = expired_tibs
# asset.not_null = expired_sectors
# asset.not_null = removed_tibs
# asset.not_null = removed_sectors
# asset.assert = onboarded_tibs >= 0
# asset.assert = onboarded_sectors >= 0
# asset.assert = terminated_tibs >= 0
# asset.assert = terminated_sectors >= 0
# asset.assert = expired_tibs >= 0
# asset.assert = expired_sectors >= 0
# asset.assert = removed_tibs >= 0
# asset.assert = removed_sectors >= 0

from fdp.bigquery import materialize_query

ASSET_KEY = "raw.storage_provider_sector_lifecycle"
SCHEMA = "raw"
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
    e.miner_id as provider_id,
    cast(
        sum(
            case
                when e.event in ('SECTOR_ADDED', 'COMMIT_CAPACITY_ADDED')
                    then ms.sector_size
                else 0
            end
        ) as float64
    ) / pow(1024, 4) as onboarded_tibs,
    countif(e.event in ('SECTOR_ADDED', 'COMMIT_CAPACITY_ADDED'))
        as onboarded_sectors,
    cast(
        sum(
            case
                when e.event = 'SECTOR_TERMINATED' then ms.sector_size
                else 0
            end
        ) as float64
    ) / pow(1024, 4) as terminated_tibs,
    countif(e.event = 'SECTOR_TERMINATED') as terminated_sectors,
    cast(
        sum(
            case
                when e.event = 'SECTOR_EXPIRED' then ms.sector_size
                else 0
            end
        ) as float64
    ) / pow(1024, 4) as expired_tibs,
    countif(e.event = 'SECTOR_EXPIRED') as expired_sectors,
    cast(
        sum(
            case
                when e.event in ('SECTOR_TERMINATED', 'SECTOR_EXPIRED')
                    then ms.sector_size
                else 0
            end
        ) as float64
    ) / pow(1024, 4) as removed_tibs,
    countif(e.event in ('SECTOR_TERMINATED', 'SECTOR_EXPIRED'))
        as removed_sectors
from `lily-data.lily.miner_sector_events` as e
join miner_sizes as ms
    using (miner_id)
where e.event in (
    'SECTOR_ADDED',
    'COMMIT_CAPACITY_ADDED',
    'SECTOR_TERMINATED',
    'SECTOR_EXPIRED'
)
group by 1, 2
order by 1, 2
""".strip()


def sector_lifecycle() -> None:
    materialize_query(ASSET_KEY, QUERY, schema=SCHEMA)
