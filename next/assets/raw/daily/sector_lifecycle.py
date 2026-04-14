# asset.description = Daily Filecoin sector lifecycle bytes from sector events.

# asset.materialization = custom

# asset.not_null = date
# asset.unique = date

from fdp.bigquery import materialize_query

ASSET_KEY = "raw.daily_sector_lifecycle"
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
    sum(
        case
            when e.event in ('SECTOR_ADDED', 'COMMIT_CAPACITY_ADDED')
                then ms.sector_size
            else 0
        end
    ) as onboarded_bytes,
    countif(e.event in ('SECTOR_ADDED', 'COMMIT_CAPACITY_ADDED'))
        as onboarded_sectors,
    sum(
        case
            when e.event = 'SECTOR_TERMINATED' then ms.sector_size
            else 0
        end
    ) as terminated_bytes,
    countif(e.event = 'SECTOR_TERMINATED') as terminated_sectors,
    sum(
        case
            when e.event = 'SECTOR_EXPIRED' then ms.sector_size
            else 0
        end
    ) as expired_bytes,
    countif(e.event = 'SECTOR_EXPIRED') as expired_sectors,
    sum(
        case
            when e.event in ('SECTOR_TERMINATED', 'SECTOR_EXPIRED')
                then ms.sector_size
            else 0
        end
    ) as removed_bytes,
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
group by 1
order by 1
""".strip()


def sector_lifecycle() -> None:
    materialize_query(ASSET_KEY, QUERY, schema=SCHEMA)
