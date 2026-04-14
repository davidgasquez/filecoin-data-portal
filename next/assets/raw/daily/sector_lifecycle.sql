-- asset.description = Daily Filecoin sector lifecycle bytes from sector events.
-- asset.resource = bigquery.lily

-- asset.not_null = date
-- asset.unique = date

with miner_sizes as (
    select
        miner_id,
        max(cast(sector_size as int64)) as sector_size
    from `miner_infos`
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
from `miner_sector_events` as e
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
