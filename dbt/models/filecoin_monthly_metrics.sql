with deal_metrics as (
    select
        time_bucket(interval '1 month', cast(sector_start_at as date), date '2020-09-01') as date,
        sum(padded_piece_size_tibs / 1024) as onboarded_data_pibs,
        sum(padded_piece_size_tibs / 1024) filter (piece_client_replication_order = 1 and piece_provider_replication_order = 1) as unique_data_onboarded_data_pibs,
        unique_data_onboarded_data_pibs / onboarded_data_pibs as unique_data_onboarded_ratio,
        approx_count_distinct(deal_id) as deals,
        count(piece_cid) as piece_cids,
        approx_count_distinct(piece_cid) as unique_piece_cids,
        approx_count_distinct(client_id) as unique_deal_making_clients,
        approx_count_distinct(provider_id) as unique_deal_making_providers
    from {{ ref('filecoin_state_market_deals') }}
    where 1 = 1
        and sector_start_at is not null
    group by 1
    order by 1
),

daily_to_monthly_aggs as (
    select
        time_bucket(interval '1 month', date, date '2020-09-01') as date,
        sum(daily_sector_onboarding_count) as sector_onboarding_count,
        sum(daily_sector_onboarding_raw_power_tibs) / 1024 as sector_onboarding_raw_power_pibs,
        sum(daily_sector_onboarding_quality_adjusted_power_tibs) / 1024 as sector_onboarding_quality_adjusted_power_pibs,
        sum(daily_new_terminated_raw_power_tibs) / 1024 as sector_terminated_raw_power_pibs,
        sum(daily_new_terminated_quality_adjusted_power_tibs) / 1024 as sector_terminated_quality_adjusted_power_pibs
    from {{ ref('filecoin_daily_storage_providers_metrics') }}
    group by 1
)

select
    deal_metrics.date,
    onboarded_data_pibs,
    unique_data_onboarded_data_pibs,
    unique_data_onboarded_ratio,
    deals,
    piece_cids,
    unique_piece_cids,
    unique_deal_making_clients,
    unique_deal_making_providers,
    sector_onboarding_count,
    sector_onboarding_raw_power_pibs,
    sector_onboarding_quality_adjusted_power_pibs,
    sector_terminated_raw_power_pibs,
    sector_terminated_quality_adjusted_power_pibs
from deal_metrics
left join daily_to_monthly_aggs
    on deal_metrics.date = daily_to_monthly_aggs.date
order by deal_metrics.date desc
