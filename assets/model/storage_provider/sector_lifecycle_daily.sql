-- asset.description = Daily storage provider sector lifecycle totals.

-- asset.resource = bigquery.lily

-- asset.column = date | UTC date.
-- asset.column = provider_id | Filecoin storage provider actor id address.
-- asset.column = onboarded_tibs | Raw data onboarded on the date, in tebibytes.
-- asset.column = onboarded_sectors | Sectors onboarded on the date.
-- asset.column = terminated_tibs | Raw data terminated on the date, in tebibytes.
-- asset.column = terminated_sectors | Sectors terminated on the date.
-- asset.column = expired_tibs | Raw data expired on the date, in tebibytes.
-- asset.column = expired_sectors | Sectors expired on the date.
-- asset.column = removed_tibs | Raw data removed on the date, in tebibytes.
-- asset.column = removed_sectors | Sectors removed on the date.

-- asset.not_null = date
-- asset.not_null = provider_id
-- asset.not_null = onboarded_tibs
-- asset.not_null = onboarded_sectors
-- asset.not_null = terminated_tibs
-- asset.not_null = terminated_sectors
-- asset.not_null = expired_tibs
-- asset.not_null = expired_sectors
-- asset.not_null = removed_tibs
-- asset.not_null = removed_sectors
-- asset.assert = onboarded_tibs >= 0
-- asset.assert = onboarded_sectors >= 0
-- asset.assert = terminated_tibs >= 0
-- asset.assert = terminated_sectors >= 0
-- asset.assert = expired_tibs >= 0
-- asset.assert = expired_sectors >= 0
-- asset.assert = removed_tibs >= 0
-- asset.assert = removed_sectors >= 0

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
from `miner_sector_events` as e
join miner_sizes as ms
    using (miner_id)
where e.event in (
    'SECTOR_ADDED',
    'COMMIT_CAPACITY_ADDED',
    'SECTOR_TERMINATED',
    'SECTOR_EXPIRED'
)
group by 1, 2
