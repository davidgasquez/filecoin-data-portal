select
    provider_id,
    sum(piece_size_tibs) as onboarded_tibs,
    count(distinct deal_id) as total_deals,
    count(distinct client_id) as total_clients,
    min(sector_start_at) as first_deal_at,
    max(sector_start_at) as last_deal_at,
from {{ ref("filecoin_state_market_deals") }}
group by 1
order by 2 desc
