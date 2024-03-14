with storage_provider_location as (
    select * from {{ ref("filecoin_storage_providers_location") }}
),

stats as (
    select
        provider_id,
        count(distinct deal_id) as total_deals,
        count(distinct provider_id) as total_unique_providers,
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
        sum(case when sector_start_at > current_date() - interval '30 days' then unpadded_piece_size_tibs else 0 end) as data_uploaded_tibs_30d
    from {{ ref("filecoin_state_market_deals") }}
    group by 1
    order by 2 desc
)

select
    stats.provider_id,
    stats.total_deals,
    stats.total_unique_providers,
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
    storage_provider_location.region,
    storage_provider_location.country,
    storage_provider_location.latitude,
    storage_provider_location.longitude
from stats
left join storage_provider_location
    on stats.provider_id = storage_provider_location.provider_id
