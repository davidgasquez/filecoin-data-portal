with storage_provider_location as (
    select * from {{ ref("filecoin_storage_providers_location") }}
),

stats as (
    select
        provider_id,
        sum(padded_piece_size_bytes) as onboarded_tibs,
        count(distinct deal_id) as total_deals,
        count(distinct client_id) as total_clients,
        min(sector_start_at) as first_deal_at,
        max(sector_start_at) as last_deal_at,
    from {{ ref("filecoin_state_market_deals") }}
    group by 1
    order by 2 desc
)

select
    stats.provider_id,
    stats.onboarded_tibs,
    stats.total_deals,
    stats.total_clients,
    stats.first_deal_at,
    stats.last_deal_at,
    storage_provider_location.region,
    storage_provider_location.country,
    storage_provider_location.latitude,
    storage_provider_location.longitude
from stats
left join storage_provider_location
    on stats.provider_id = storage_provider_location.provider_id
