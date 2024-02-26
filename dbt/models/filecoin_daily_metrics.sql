with deal_metrics as (
    select
        date_trunc('day', sector_start_at) as date,
        sum(piece_size_tibs) as onboarded_tibs
    from {{ ref('filecoin_state_market_deals') }}
    where
        sector_start_epoch > 0 and slash_epoch = -1
        and sector_start_at::date < current_date
        and sector_start_at::date > '2022-01-01'
    group by 1
    order by 1
)

select
    date,
    onboarded_tibs,
    sum(onboarded_tibs) over (order by date) as cumulative_onboarded_tibs
from deal_metrics
