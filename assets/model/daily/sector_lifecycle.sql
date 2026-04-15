-- asset.description = Daily sector lifecycle totals.

-- asset.depends = raw.daily_sector_lifecycle

-- asset.column = date | UTC date.
-- asset.column = onboarded_pibs | Raw sector data onboarded on the date, in pebibytes.
-- asset.column = terminated_pibs | Raw sector data terminated on the date, in pebibytes.
-- asset.column = expired_pibs | Raw sector data expired on the date, in pebibytes.
-- asset.column = removed_pibs | Raw sector data removed on the date, in pebibytes.

-- asset.not_null = date
-- asset.not_null = onboarded_pibs
-- asset.not_null = terminated_pibs
-- asset.not_null = expired_pibs
-- asset.not_null = removed_pibs
-- asset.unique = date

select
    date,
    cast(onboarded_bytes as double) / pow(1024, 5) as onboarded_pibs,
    cast(terminated_bytes as double) / pow(1024, 5) as terminated_pibs,
    cast(expired_bytes as double) / pow(1024, 5) as expired_pibs,
    cast(removed_bytes as double) / pow(1024, 5) as removed_pibs
from raw.daily_sector_lifecycle
order by date desc
