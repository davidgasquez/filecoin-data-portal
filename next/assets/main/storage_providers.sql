-- asset.description = Published storage providers.

-- asset.depends = raw.storage_provider_current_info
-- asset.depends = model.storage_provider_power_daily
-- asset.depends = model.storage_provider_sector_lifecycle_daily
-- asset.depends = raw.verified_registry_claims

-- asset.column = provider_id | Filecoin storage provider actor id address.
-- asset.column = owner_id | Current owner actor id address.
-- asset.column = worker_id | Current worker actor id address.
-- asset.column = peer_id | Current libp2p peer id.
-- asset.column = control_addresses | Current JSON array of control addresses.
-- asset.column = multi_addresses | Current JSON array of multiaddrs.
-- asset.column = sector_size | Current sector size in bytes.
-- asset.column = raw_power_tibs | Current raw byte power, in tebibytes.
-- asset.column = quality_adjusted_power_tibs | Current quality adjusted power, in tebibytes.
-- asset.column = has_power | Whether the provider currently has positive power.
-- asset.column = has_sector_activity | Whether the provider has sector lifecycle activity.
-- asset.column = has_verified_claims | Whether the provider has successful verified claims.
-- asset.column = first_sector_activity_date | First date with sector lifecycle activity.
-- asset.column = last_sector_activity_date | Most recent date with sector lifecycle activity.
-- asset.column = first_verified_claim_at | First successful verified claim timestamp.
-- asset.column = last_verified_claim_at | Most recent successful verified claim timestamp.
-- asset.column = verified_claims | Total successful verified claims.
-- asset.column = verified_clients | Clients with at least one successful verified claim.
-- asset.column = verified_data_onboarded_tibs | Verified data successfully claimed, in tebibytes.

-- asset.not_null = provider_id
-- asset.not_null = has_power
-- asset.not_null = has_sector_activity
-- asset.not_null = has_verified_claims
-- asset.unique = provider_id

with current_power as (
    select
        provider_id,
        raw_power_tibs,
        quality_adjusted_power_tibs,
        has_power
    from model.storage_provider_power_daily
    where date = (select max(date) from model.storage_provider_power_daily)
),
sector_activity as (
    select
        provider_id,
        min(date) as first_sector_activity_date,
        max(date) as last_sector_activity_date,
        true as has_sector_activity
    from model.storage_provider_sector_lifecycle_daily
    group by 1
),
verified_claim_activity as (
    select
        'f0' || cast(provider_id as varchar) as provider_id,
        min(to_timestamp((claim_epoch * 30) + 1598306400)) as first_verified_claim_at,
        max(to_timestamp((claim_epoch * 30) + 1598306400)) as last_verified_claim_at,
        count(*) as verified_claims,
        count(distinct client_id) as verified_clients,
        cast(sum(piece_size_bytes) as double) / power(1024, 4)
            as verified_data_onboarded_tibs,
        true as has_verified_claims
    from raw.verified_registry_claims
    group by 1
),
providers as (
    select distinct provider_id from model.storage_provider_sector_lifecycle_daily
    union
    select distinct 'f0' || cast(provider_id as varchar) as provider_id
    from raw.verified_registry_claims
    union
    select provider_id from current_power
)
select
    providers.provider_id,
    info.owner_id,
    info.worker_id,
    info.peer_id,
    info.control_addresses,
    info.multi_addresses,
    info.sector_size,
    current_power.raw_power_tibs,
    current_power.quality_adjusted_power_tibs,
    coalesce(current_power.has_power, false) as has_power,
    coalesce(sector_activity.has_sector_activity, false) as has_sector_activity,
    coalesce(verified_claim_activity.has_verified_claims, false) as has_verified_claims,
    sector_activity.first_sector_activity_date,
    sector_activity.last_sector_activity_date,
    verified_claim_activity.first_verified_claim_at,
    verified_claim_activity.last_verified_claim_at,
    verified_claim_activity.verified_claims,
    verified_claim_activity.verified_clients,
    verified_claim_activity.verified_data_onboarded_tibs
from providers
left join raw.storage_provider_current_info as info
    using (provider_id)
left join current_power
    using (provider_id)
left join sector_activity
    using (provider_id)
left join verified_claim_activity
    using (provider_id)
order by last_verified_claim_at desc
