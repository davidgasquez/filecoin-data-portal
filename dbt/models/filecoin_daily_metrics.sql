with deal_metrics as (
    select
        date_trunc('day', start_at) as date,
        sum(padded_piece_size_tib) as proposed_data_tibs,
        count(distinct deal_id) as proposed_deals,
        count(distinct client_id) as unique_clients,
        count(distinct provider_id) as unique_providers
    from {{ ref('filecoin_state_market_deals') }}
    where 1 = 1
        and cast(start_at as date) < current_date
    group by 1
    order by 1
)

select
    date,
    proposed_data_tibs,
    sum(proposed_data_tibs) over (order by date) as cumulative_proposed_data_tibs,
    proposed_deals,
    unique_clients,
    unique_providers
from deal_metrics
