with storage_provider_location as (
    select * from {{ ref("filecoin_storage_providers_location") }}
),

stats as (
    select
        provider_id,
        count(distinct deal_id) as total_deals,
        count(distinct deal_id) filter (where is_verified) as total_verified_deals,
        count(distinct deal_id) filter (where is_active) as total_active_deals,
        count(distinct deal_id) filter (where is_active and is_verified) as total_active_verified_deals,

        count(distinct piece_cid) as total_unique_piece_cids,
        count(distinct piece_cid) filter (where is_verified) as total_verified_unique_piece_cids,
        count(distinct piece_cid) filter (where is_active) as total_active_unique_piece_cids,
        count(distinct piece_cid) filter (where is_active and is_verified) as total_active_verified_unique_piece_cids,

        sum(unpadded_piece_size_tibs) as total_data_uploaded_tibs,
        sum(unpadded_piece_size_tibs) filter (where is_active) as total_active_data_uploaded_tibs,
        sum(unpadded_piece_size_tibs) filter (piece_provider_replication_order = 1) as unique_data_uploaded_tibs,
        sum(unpadded_piece_size_tibs) filter (where is_active and piece_provider_replication_order = 1) as unique_active_data_uploaded_tibs,
        unique_data_uploaded_tibs / sum(unpadded_piece_size_tibs) as unique_data_uploaded_ratio,

        count(distinct client_id) as total_unique_clients,
        count(distinct client_id) filter (where is_active) as total_active_unique_clients,
        count(distinct client_id) filter (where is_active and is_verified) as total_active_verified_unique_clients,

        min(sector_start_at) as first_deal_at,
        min(case when is_active then sector_start_at else null end) as first_active_deal_at,
        max(sector_start_at) as last_deal_at,
        max(case when is_active then sector_start_at else null end) as last_active_deal_at,

        sum(unpadded_piece_size_tibs) filter(where sector_start_at > current_date() - interval '30 days') as data_uploaded_tibs_30d,
        sum(unpadded_piece_size_tibs) filter(where sector_start_at > current_date() - interval '6 months') as data_uploaded_tibs_6m,
        sum(unpadded_piece_size_tibs) filter(where sector_start_at > current_date() - interval '1 year') as data_uploaded_tibs_1y,
    from {{ ref("filecoin_state_market_deals") }}
    where sector_start_epoch is not null
    group by 1
),

reputation_data as (
    select
        address as provider_id,
        if(reachability = 'reachable', true, false) as is_reachable,
        name as provider_name,
        uptimeaverage as uptime_average,
        score as score,
        rank
    from {{ source('raw_assets', 'raw_storage_providers_reputation') }}
),

power_data as (
    select distinct
        provider_id,
        raw_power_pibs,
        quality_adjusted_power_pibs,
        verified_data_power_pibs,
    from {{ ref("filecoin_storage_providers_power") }}
    qualify row_number() over (partition by provider_id order by date desc) = 1
)

select
    stats.*,
    power_data.raw_power_pibs,
    power_data.quality_adjusted_power_pibs,
    power_data.verified_data_power_pibs,
    storage_provider_location.region,
    storage_provider_location.country,
    storage_provider_location.latitude,
    storage_provider_location.longitude,
    reputation_data.provider_name,
    reputation_data.is_reachable,
    reputation_data.uptime_average,
    reputation_data.score,
    reputation_data.rank
from stats
left join storage_provider_location on stats.provider_id = storage_provider_location.provider_id
left join reputation_data on stats.provider_id = reputation_data.provider_id
left join power_data on stats.provider_id = power_data.provider_id
