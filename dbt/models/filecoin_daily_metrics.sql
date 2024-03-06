with deal_metrics as (
    select
        date_trunc('day', sector_start_at) as date,
        sum(padded_piece_size_tib) as onboarded_data_tibs,
        count(distinct deal_id) as deals,
        count(distinct client_id) as unique_clients,
        count(distinct provider_id) as unique_providers
    from {{ ref('filecoin_state_market_deals') }}
    where 1 = 1
        and sector_start_at is not null
    group by 1
    order by 1
)

select
    date,
    onboarded_data_tibs,
    deals,
    unique_clients,
    unique_providers
from deal_metrics
order by date desc
