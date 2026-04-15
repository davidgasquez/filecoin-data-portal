-- asset.description = Published daily storage providers metrics.

-- asset.depends = model.storage_provider_power_daily
-- asset.depends = model.storage_provider_sector_lifecycle_daily
-- asset.depends = model.daily_verified_claims

-- asset.column = date | UTC date.
-- asset.column = provider_id | Filecoin storage provider actor id address.
-- asset.column = raw_power_tibs | End-of-day raw byte power, in tebibytes.
-- asset.column = quality_adjusted_power_tibs | End-of-day quality adjusted power, in tebibytes.
-- asset.column = has_power | Whether the provider had positive power at end of day.
-- asset.column = onboarded_tibs | Raw data onboarded on the date, in tebibytes.
-- asset.column = onboarded_sectors | Sectors onboarded on the date.
-- asset.column = terminated_tibs | Raw data terminated on the date, in tebibytes.
-- asset.column = terminated_sectors | Sectors terminated on the date.
-- asset.column = expired_tibs | Raw data expired on the date, in tebibytes.
-- asset.column = expired_sectors | Sectors expired on the date.
-- asset.column = removed_tibs | Raw data removed on the date, in tebibytes.
-- asset.column = removed_sectors | Sectors removed on the date.
-- asset.column = verified_data_onboarded_tibs | Verified data claimed on the date, in tebibytes.
-- asset.column = verified_claims | Successful verified claims on the date.
-- asset.column = verified_clients | Clients with at least one successful verified claim on the date.

-- asset.not_null = date
-- asset.not_null = provider_id
-- asset.not_null = raw_power_tibs
-- asset.not_null = quality_adjusted_power_tibs
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
-- asset.not_null = verified_clients

with verified_claims as (
    select
        date,
        provider_id,
        sum(verified_data_onboarded_tibs) as verified_data_onboarded_tibs,
        sum(verified_claims) as verified_claims,
        count(distinct client_id) as verified_clients
    from model.daily_verified_claims
    group by 1, 2
),
provider_days as (
    select date, provider_id from model.storage_provider_power_daily
    union
    select date, provider_id from model.storage_provider_sector_lifecycle_daily
    union
    select date, provider_id from verified_claims
)
select
    provider_days.date,
    provider_days.provider_id,
    coalesce(power.raw_power_tibs, 0) as raw_power_tibs,
    coalesce(power.quality_adjusted_power_tibs, 0) as quality_adjusted_power_tibs,
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
    coalesce(verified_claims.verified_clients, 0) as verified_clients
from provider_days
left join model.storage_provider_power_daily as power
    using (date, provider_id)
left join model.storage_provider_sector_lifecycle_daily as sector_lifecycle
    using (date, provider_id)
left join verified_claims
    using (date, provider_id)
order by date desc
