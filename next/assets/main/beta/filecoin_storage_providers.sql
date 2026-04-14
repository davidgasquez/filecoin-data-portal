-- asset.description = Historically active Filecoin storage providers enriched with current miner info, current power, market deal activity, and verified claim activity.

-- asset.depends = raw.storage_provider_current_info
-- asset.depends = raw.storage_provider_current_power
-- asset.depends = raw.storage_provider_market_deal_activity
-- asset.depends = raw.storage_provider_sector_lifecycle
-- asset.depends = raw.storage_provider_verified_claims

-- asset.column = provider_id | Filecoin storage provider miner actor id address.
-- asset.column = owner_id | Current owner id address from the latest Lily miner info snapshot, if available.
-- asset.column = worker_id | Current worker id address from the latest Lily miner info snapshot, if available.
-- asset.column = peer_id | Current libp2p peer id from the latest Lily miner info snapshot, if available.
-- asset.column = control_addresses | Current JSON array of control addresses from the latest Lily miner info snapshot, if available.
-- asset.column = multi_addresses | Current JSON array of multiaddrs from the latest Lily miner info snapshot, if available.
-- asset.column = sector_size | Current sector size in bytes from the latest Lily miner info snapshot, if available.
-- asset.column = current_raw_power_tibs | Latest observed raw byte power for the provider, in tebibytes, if currently positive.
-- asset.column = current_quality_adjusted_power_tibs | Latest observed quality adjusted power for the provider, in tebibytes, if currently positive.
-- asset.column = has_current_power | Whether the provider currently has positive raw or quality adjusted power.
-- asset.column = has_sector_activity | Whether the provider has at least one sector lifecycle event in the provider daily sector lifecycle table.
-- asset.column = has_market_deals | Whether the provider appears in Lily market deal proposals.
-- asset.column = has_verified_claims | Whether the provider has at least one successful verified claim.
-- asset.column = first_sector_activity_date | First day with sector lifecycle activity for the provider, if available.
-- asset.column = last_sector_activity_date | Most recent day with sector lifecycle activity for the provider, if available.
-- asset.column = first_market_deal_start_date | First observed storage deal start date for the provider, if available.
-- asset.column = last_market_deal_start_date | Most recent storage deal start date for the provider, if available.
-- asset.column = first_verified_claim_date | First day with a successful verified claim for the provider, if available.
-- asset.column = last_verified_claim_date | Most recent day with a successful verified claim for the provider, if available.
-- asset.column = total_verified_claims | Total successful verified claims observed for the provider.
-- asset.column = total_verified_data_onboarded_tibs | Total verified data successfully claimed by the provider, in tebibytes.
-- asset.not_null = provider_id
-- asset.not_null = has_current_power
-- asset.not_null = has_sector_activity
-- asset.not_null = has_market_deals
-- asset.not_null = has_verified_claims
-- asset.unique = provider_id

with sector_activity as (
    select
        provider_id,
        min(date) as first_sector_activity_date,
        max(date) as last_sector_activity_date,
        true as has_sector_activity
    from raw.storage_provider_sector_lifecycle
    group by 1
),
verified_claim_activity as (
    select
        provider_id,
        min(date) as first_verified_claim_date,
        max(date) as last_verified_claim_date,
        sum(verified_claims) as total_verified_claims,
        sum(verified_data_onboarded_tibs) as total_verified_data_onboarded_tibs,
        true as has_verified_claims
    from raw.storage_provider_verified_claims
    group by 1
),
providers as (
    select distinct provider_id from raw.storage_provider_sector_lifecycle
    union
    select provider_id from raw.storage_provider_market_deal_activity
    union
    select distinct provider_id from raw.storage_provider_verified_claims
    union
    select provider_id from raw.storage_provider_current_power
)
select
    providers.provider_id,
    info.owner_id,
    info.worker_id,
    info.peer_id,
    info.control_addresses,
    info.multi_addresses,
    info.sector_size,
    current_power.current_raw_power_tibs,
    current_power.current_quality_adjusted_power_tibs,
    coalesce(current_power.has_current_power, false) as has_current_power,
    coalesce(sector_activity.has_sector_activity, false) as has_sector_activity,
    market_deal_activity.provider_id is not null as has_market_deals,
    coalesce(verified_claim_activity.has_verified_claims, false) as has_verified_claims,
    sector_activity.first_sector_activity_date,
    sector_activity.last_sector_activity_date,
    market_deal_activity.first_market_deal_start_date,
    market_deal_activity.last_market_deal_start_date,
    verified_claim_activity.first_verified_claim_date,
    verified_claim_activity.last_verified_claim_date,
    verified_claim_activity.total_verified_claims,
    verified_claim_activity.total_verified_data_onboarded_tibs
from providers
left join raw.storage_provider_current_info as info
    using (provider_id)
left join raw.storage_provider_current_power as current_power
    using (provider_id)
left join sector_activity
    using (provider_id)
left join raw.storage_provider_market_deal_activity as market_deal_activity
    using (provider_id)
left join verified_claim_activity
    using (provider_id)
order by providers.provider_id
