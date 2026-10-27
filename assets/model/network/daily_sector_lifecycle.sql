-- asset.description = Daily sector lifecycle totals.

-- asset.depends = model.network_daily_miner_sector_lifecycle

-- asset.column = date | UTC date.
-- asset.column = onboarded_pibs | Raw sector data onboarded on the date, in pebibytes.
-- asset.column = onboarded_sectors | Sectors onboarded on the date.
-- asset.column = terminated_pibs | Raw sector data terminated on the date, in pebibytes.
-- asset.column = terminated_sectors | Sectors terminated on the date.
-- asset.column = expired_pibs | Raw sector data expired on the date, in pebibytes.
-- asset.column = expired_sectors | Sectors expired on the date.
-- asset.column = removed_pibs | Raw sector data removed on the date, in pebibytes.
-- asset.column = removed_sectors | Sectors removed on the date.

-- asset.not_null = date
-- asset.not_null = onboarded_pibs
-- asset.not_null = onboarded_sectors
-- asset.not_null = terminated_pibs
-- asset.not_null = terminated_sectors
-- asset.not_null = expired_pibs
-- asset.not_null = expired_sectors
-- asset.not_null = removed_pibs
-- asset.not_null = removed_sectors
-- asset.unique = date

select
    date,
    sum(onboarded_tibs) / 1024 as onboarded_pibs,
    sum(onboarded_sectors) as onboarded_sectors,
    sum(terminated_tibs) / 1024 as terminated_pibs,
    sum(terminated_sectors) as terminated_sectors,
    sum(expired_tibs) / 1024 as expired_pibs,
    sum(expired_sectors) as expired_sectors,
    sum(removed_tibs) / 1024 as removed_pibs,
    sum(removed_sectors) as removed_sectors
from model.network_daily_miner_sector_lifecycle
group by date
order by date desc
