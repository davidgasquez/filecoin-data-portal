with date_calendar as (
  select
    cast(range as date) as day
  from range(date '2020-09-12', current_date(), interval '1 day')
),

deal_metrics as (
    select
        date_trunc('day', sector_start_at) as date,
        sum(padded_piece_size_tibs) as onboarded_data_tibs,
        count(distinct deal_id) as deals,
        count(distinct client_id) as unique_clients,
        count(distinct provider_id) as unique_providers
    from {{ ref('filecoin_state_market_deals') }}
    where 1 = 1
        and sector_start_at is not null
    group by 1
    order by 1
),

users_with_active_deals as (
    select
        dc.day,
        approx_count_distinct(deals.deal_id) as active_deals,
        approx_count_distinct(deals.client_id) as clients_with_active_deals,
        approx_count_distinct(deals.provider_id) as providers_with_active_deals
    from date_calendar as dc
    left join {{ ref('filecoin_state_market_deals') }} as deals
        on dc.day between deals.sector_start_at and least(deals.end_at, deals.slash_at)
    group by dc.day
)

select
    date,
    onboarded_data_tibs,
    deals,
    unique_clients,
    unique_providers,
    active_deals,
    clients_with_active_deals,
    providers_with_active_deals
from date_calendar
left join deal_metrics on date_calendar.day = deal_metrics.date
left join users_with_active_deals on date_calendar.day = users_with_active_deals.day
order by date desc
