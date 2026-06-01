-- asset.description = Daily Filecoin sector lifecycle bytes from sector events.
-- asset.depends = model.storage_provider_sector_lifecycle_daily

-- asset.not_null = date
-- asset.unique = date

select
    date,
    cast(sum(onboarded_tibs) * pow(1024, 4) as hugeint) as onboarded_bytes,
    sum(onboarded_sectors) as onboarded_sectors,
    cast(sum(terminated_tibs) * pow(1024, 4) as hugeint) as terminated_bytes,
    sum(terminated_sectors) as terminated_sectors,
    cast(sum(expired_tibs) * pow(1024, 4) as hugeint) as expired_bytes,
    sum(expired_sectors) as expired_sectors,
    cast(sum(removed_tibs) * pow(1024, 4) as hugeint) as removed_bytes,
    sum(removed_sectors) as removed_sectors
from model.storage_provider_sector_lifecycle_daily
group by 1
order by 1
