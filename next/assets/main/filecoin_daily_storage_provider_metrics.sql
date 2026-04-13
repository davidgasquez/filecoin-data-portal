-- asset.description = Daily Filecoin storage provider metrics from power snapshots, sector lifecycle activity, and verified claims, with sparse provider-day rows.

-- asset.depends = raw.storage_provider_power
-- asset.depends = raw.storage_provider_sector_lifecycle
-- asset.depends = raw.storage_provider_verified_claims

-- asset.column = date | UTC day for the provider metrics snapshot.
-- asset.column = provider_id | Filecoin storage provider miner actor id address.
-- asset.column = raw_power_pibs | End-of-day raw byte power for the provider, in pebibytes.
-- asset.column = quality_adj_power_pibs | End-of-day quality adjusted power for the provider, in pebibytes.
-- asset.column = has_power | Whether the provider had positive raw or quality adjusted power at end of day.
-- asset.column = onboarded_tibs | Total raw sector data onboarded by the provider on the day, in tebibytes.
-- asset.column = onboarded_sectors | Total sectors onboarded by the provider on the day.
-- asset.column = terminated_tibs | Total raw sector data terminated by the provider on the day, in tebibytes.
-- asset.column = terminated_sectors | Total sectors terminated by the provider on the day.
-- asset.column = expired_tibs | Total raw sector data expired by the provider on the day, in tebibytes.
-- asset.column = expired_sectors | Total sectors expired by the provider on the day.
-- asset.column = removed_tibs | Total raw sector data removed by the provider on the day, in tebibytes.
-- asset.column = removed_sectors | Total sectors removed by the provider on the day.
-- asset.column = verified_data_onboarded_tibs | Sum of verified piece sizes claimed by the provider on the day, in tebibytes.
-- asset.column = verified_claims | Number of successful verified registry claims by the provider on the day.
-- asset.column = unique_verified_clients | Distinct verified clients with at least one successful claim with the provider on the day.

-- asset.not_null = date
-- asset.not_null = provider_id
-- asset.not_null = raw_power_pibs
-- asset.not_null = quality_adj_power_pibs
-- asset.not_null = has_power
-- asset.not_null = onboarded_tibs
-- asset.not_null = onboarded_sectors
-- asset.not_null = terminated_tibs
-- asset.not_null = terminated_sectors
-- asset.not_null = expired_tibs
-- asset.not_null = expired_sectors
-- asset.not_null = removed_tibs
-- asset.not_null = removed_sectors
-- asset.not_null = verified_data_onboarded_tibs
-- asset.not_null = verified_claims
-- asset.not_null = unique_verified_clients

with provider_days as (
    select date, provider_id from raw.storage_provider_power
    union
    select date, provider_id from raw.storage_provider_sector_lifecycle
    union
    select date, provider_id from raw.storage_provider_verified_claims
)
select
    provider_days.date,
    provider_days.provider_id,
    coalesce(power.raw_power_pibs, 0) as raw_power_pibs,
    coalesce(power.quality_adj_power_pibs, 0) as quality_adj_power_pibs,
    coalesce(power.has_power, false) as has_power,
    coalesce(sector_lifecycle.onboarded_tibs, 0) as onboarded_tibs,
    coalesce(sector_lifecycle.onboarded_sectors, 0) as onboarded_sectors,
    coalesce(sector_lifecycle.terminated_tibs, 0) as terminated_tibs,
    coalesce(sector_lifecycle.terminated_sectors, 0) as terminated_sectors,
    coalesce(sector_lifecycle.expired_tibs, 0) as expired_tibs,
    coalesce(sector_lifecycle.expired_sectors, 0) as expired_sectors,
    coalesce(sector_lifecycle.removed_tibs, 0) as removed_tibs,
    coalesce(sector_lifecycle.removed_sectors, 0) as removed_sectors,
    coalesce(verified_claims.verified_data_onboarded_tibs, 0) as verified_data_onboarded_tibs,
    coalesce(verified_claims.verified_claims, 0) as verified_claims,
    coalesce(verified_claims.unique_verified_clients, 0) as unique_verified_clients
from provider_days
left join raw.storage_provider_power as power
    using (date, provider_id)
left join raw.storage_provider_sector_lifecycle as sector_lifecycle
    using (date, provider_id)
left join raw.storage_provider_verified_claims as verified_claims
    using (date, provider_id)
order by date desc, provider_id
