with storage_provider_location as (
    select * from {{ ref("filecoin_storage_providers_location") }}
),

stats as (
    select
        provider_id,
        count(distinct deal_id) as total_deals,
        count(distinct client_id) as total_unique_clients,
        count(distinct piece_cid) as total_unique_piece_cids,
        sum(unpadded_piece_size_tibs) as total_data_uploaded_tibs,
        sum(case when is_active then unpadded_piece_size_tibs else 0 end) as total_active_data_uploaded_tibs,
        count(case when is_active then 1 else 0 end) as total_active_deals,
        count(case when is_verified then 1 else 0 end) as total_verified_deals,
        count(case when is_active and is_verified then 1 else 0 end) as total_active_verified_deals,
        min(sector_start_at) as first_deal_at,
        min(case when is_active then sector_start_at else null end) as first_active_deal_at,
        max(sector_start_at) as last_deal_at,
        max(case when is_active then sector_start_at else null end) as last_active_deal_at,
        sum(case when sector_start_at > current_date() - interval '30 days' then unpadded_piece_size_tibs else 0 end) as data_uploaded_tibs_30d,
        sum(unpadded_piece_size_tibs) filter (piece_provider_replication_order = 1) as unique_data_uploaded_tibs,
        unique_data_uploaded_tibs / sum(unpadded_piece_size_tibs) as unique_data_uploaded_percentage
    from {{ ref("filecoin_state_market_deals") }}
    group by 1
    order by 2 desc
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
)

select
    stats.provider_id,
    stats.total_deals,
    stats.total_unique_clients,
    stats.total_unique_piece_cids,
    stats.total_data_uploaded_tibs,
    stats.total_active_data_uploaded_tibs,
    stats.total_active_deals,
    stats.total_verified_deals,
    stats.total_active_verified_deals,
    stats.first_deal_at,
    stats.first_active_deal_at,
    stats.last_deal_at,
    stats.last_active_deal_at,
    stats.data_uploaded_tibs_30d,
    stats.unique_data_uploaded_tibs,
    stats.unique_data_uploaded_percentage,
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
