with date_calendar as (
  select
    cast(range as date) as date
  from range(date '2020-09-12', current_date(), interval '1 day')
),

deal_metrics as (
    select
        cast(sector_start_at as date) as date,
        client_id,
        sum(padded_piece_size_tibs) as onboarded_data_tibs,
        approx_count_distinct(deal_id) as deals,
        approx_count_distinct(piece_cid) as unique_piece_cids,
        approx_count_distinct(provider_id) as unique_deal_making_providers
    from {{ ref('filecoin_state_market_deals') }}
    where 1 = 1
        and sector_start_at is not null
        and client_id is not null
    group by 1, 2
),

deal_ends as (
    select
        cast(end_at as date) as date,
        client_id,
        approx_count_distinct(deal_id) as deal_ends,
        coalesce(sum(padded_piece_size_tibs), 0) as ended_data_tibs
    from {{ ref('filecoin_state_market_deals') }}
    where 1 = 1
        and end_at is not null
        and client_id is not null
    group by 1, 2
),

datacap_allocations as (
    select
        cast(height_at as date) as date,
        client_id,
        sum(allowance_tibs) as datacap_allowance_tibs
    from {{ ref('filecoin_clients_datacap_allowances') }}
    group by all
    having client_id is not null
),

active_deal_data as (
    select
        dc.date,
        deals.client_id,
        sum(deals.padded_piece_size_tibs) as active_data_tibs
    from date_calendar as dc
    left join {{ ref('filecoin_state_market_deals') }} as deals
        on (deals.sector_start_at <= dc.date)
        and (least(deals.end_at, deals.slash_at) >= dc.date)
        and deals.client_id is not null
    group by dc.date, deals.client_id
)

select
    ad.date,
    ad.client_id,

    -- Deal Metrics
    coalesce(dm.onboarded_data_tibs, 0) as onboarded_data_tibs,
    coalesce(dm.deals, 0) as deals,
    coalesce(dm.unique_piece_cids, 0) as unique_piece_cids,
    coalesce(dm.unique_deal_making_providers, 0) as unique_deal_making_providers,
    coalesce(de.deal_ends, 0) as deal_ends,
    coalesce(de.ended_data_tibs, 0) as ended_data_tibs,

    -- Active Deal Data
    coalesce(ad.active_data_tibs, 0) as active_data_tibs,

    -- Datacap Allocation
    coalesce(da.datacap_allowance_tibs, 0) as datacap_allowance_tibs,

from active_deal_data ad
left join deal_metrics dm on ad.date = dm.date and ad.client_id = dm.client_id
left join deal_ends de on ad.date = de.date and ad.client_id = de.client_id
left join datacap_allocations da on ad.date = da.date and ad.client_id = da.client_id
where ad.date >= '2020-09-12'
order by ad.date desc
