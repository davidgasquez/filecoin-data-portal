{% macro filecoin_periodic_metrics(period) %}

{% set period_lookback = 365 if period == 'day' else 52 if period == 'week' else 12 if period == 'month' else 4 if period == 'quarter' else 1 %}

with date_calendar as (
    select
        cast(range as date) as date
    from range(date '2020-10-01', current_date(), interval '1 {{ period }}')
),

deal_metrics as (
    select
        time_bucket(interval '1 {{ period }}', sector_start_at, date '2020-10-01') as date,
        sum(padded_piece_size_tibs / 1024) as onboarded_data_pibs,
        sum(padded_piece_size_tibs / 1024) filter (piece_client_replication_order = 1 and piece_provider_replication_order = 1) as unique_data_onboarded_data_pibs,
        sum(padded_piece_size_tibs / 1024) filter (deal_storage_cost_fil > 0.001) as onboarded_data_pibs_with_payments,
        coalesce(sum(deal_storage_cost_fil), 0.0) as deal_storage_cost_fil,
        unique_data_onboarded_data_pibs / onboarded_data_pibs as unique_data_onboarded_ratio,
        approx_count_distinct(deal_id) as deals,
        approx_count_distinct(deal_id) filter (is_verified) as verified_deals,
        approx_count_distinct(deal_id) filter (not is_verified) as regular_deals,
        approx_count_distinct(piece_cid) as unique_piece_cids,
        approx_count_distinct(client_id) as unique_deal_making_clients,
        approx_count_distinct(provider_id) as unique_deal_making_providers,
        avg(piece_replication_factor) as average_piece_replication_factor
    from {{ ref('filecoin_state_market_deals') }}
    where 1 = 1
        and sector_start_at is not null
    group by 1
    order by 1
),

users_with_active_deals as (
    select
        dc.date,
        sum(padded_piece_size_tibs / 1024) as data_on_active_deals_pibs,
        sum(padded_piece_size_tibs / 1024) filter (piece_client_replication_order = 1 and piece_provider_replication_order = 1) as unique_data_on_active_deals_pibs,
        approx_count_distinct(deals.deal_id) as active_deals,
        approx_count_distinct(deals.client_id) as clients_with_active_deals,
        approx_count_distinct(deals.provider_id) as providers_with_active_deals,
        mean(end_epoch - sector_start_epoch) // 2880 as mean_deal_duration_days,
        mean(end_epoch - sector_start_epoch) filter (is_verified) // 2880 as mean_verified_deal_duration_days,
        mean(end_epoch - sector_start_epoch) filter (not is_verified) // 2880 as mean_regular_deal_duration_days,
        avg(piece_replication_factor) as average_piece_replication_factor_active_deals
    from date_calendar as dc
    left join {{ ref('filecoin_state_market_deals') }} as deals
        on (deals.sector_start_at <= dc.date + interval '1 {{ period }}')
        and (least(deals.end_at, deals.slash_at) >= dc.date)
    group by dc.date
),

deal_ends as (
    select
        time_bucket(interval '1 {{ period }}', end_at, date '2020-10-01') as date,
        approx_count_distinct(deal_id) as deal_ends,
        coalesce(sum(padded_piece_size_tibs / 1024), 0) as ended_data_pibs
    from {{ ref('filecoin_state_market_deals') }}
    where 1 = 1
        and sector_start_at is not null
    group by 1
    order by 1
),

deal_slashes as (
    select
        time_bucket(interval '1 {{ period }}', slash_at, date '2020-10-01') as date,
        approx_count_distinct(deal_id) as deal_slashes,
        coalesce(sum(padded_piece_size_tibs / 1024), 0) as slashed_data_pibs
    from {{ ref('filecoin_state_market_deals') }}
    where 1 = 1
        and sector_start_at is not null
    group by 1
    order by 1
),

provider_metrics as (
    select
        date,
        sum(raw_power_pibs) as raw_power_pibs,
        sum(quality_adjusted_power_pibs) as quality_adjusted_power_pibs,
        sum(verified_data_power_pibs) as verified_data_power_pibs,
        sum(balance) as storage_providers_balance,
        sum(initial_pledge) as storage_providers_initial_pledge,
        sum(locked_funds) as storage_providers_locked_funds,
        sum(pre_commit_deposits) as storage_providers_pre_commit_deposits,
        sum(provider_collateral) as storage_providers_collateral,
        sum(fee_debt) as storage_providers_fee_debt,
        sum(daily_blocks_mined) as storage_providers_blocks_mined,
        sum(daily_win_count) as storage_providers_win_count,
        sum(daily_rewards) as storage_providers_rewards,
        sum(daily_sector_onboarding_count) as sector_onboarding_count,
        sum(daily_sector_onboarding_raw_power_tibs) / 1024 as sector_onboarding_raw_power_pibs,
        sum(daily_sector_onboarding_quality_adjusted_power_tibs) / 1024 as sector_onboarding_quality_adjusted_power_pibs,
        sum(daily_new_sector_terminated_raw_power_tibs) / 1024 as sector_terminated_raw_power_pibs,
        sum(daily_new_sector_terminated_quality_adjusted_power_tibs) / 1024 as sector_terminated_quality_adjusted_power_pibs,
        sum(daily_new_sector_extend_raw_power_tibs) / 1024 as sector_extended_raw_power_pibs,
        sum(daily_new_sector_extend_quality_adjusted_power_tibs) / 1024 as sector_extended_quality_adjusted_power_pibs,
        sum(daily_new_sector_fault_raw_power_tibs) / 1024 as sector_fault_raw_power_pibs,
        sum(daily_new_sector_fault_quality_adjusted_power_tibs) / 1024 as sector_fault_quality_adjusted_power_pibs,
        sum(daily_new_sector_recover_raw_power_tibs) / 1024 as sector_recover_raw_power_pibs,
        sum(daily_new_sector_recover_quality_adjusted_power_tibs) / 1024 as sector_recover_quality_adjusted_power_pibs,
        sum(daily_new_sector_expire_raw_power_tibs) / 1024 as sector_expire_raw_power_pibs,
        sum(daily_new_sector_expire_quality_adjusted_power_tibs) / 1024 as sector_expire_quality_adjusted_power_pibs,
        sum(daily_new_sector_snap_raw_power_tibs) / 1024 as sector_snap_raw_power_pibs,
        sum(daily_new_sector_snap_quality_adjusted_power_tibs) / 1024 as sector_snap_quality_adjusted_power_pibs,
        sum(active_sectors) as active_sector_count,
        count(distinct provider_id) filter (raw_power_pibs > 0) as providers_with_power,
        sum(commit_capacity_added_events_count) as commit_capacity_added_events_count,
        sum(precommit_added_events_count) as precommit_added_events_count,
        sum(sector_added_events_count) as sector_added_events_count,
        sum(sector_extended_events_count) as sector_extended_events_count,
        sum(sector_faulted_events_count) as sector_faulted_events_count,
        sum(sector_recovered_events_count) as sector_recovered_events_count,
        sum(sector_recovering_events_count) as sector_recovering_events_count,
        sum(sector_snapped_events_count) as sector_snapped_events_count,
        sum(sector_terminated_events_count) as sector_terminated_events_count
    from {{ ref('filecoin_daily_storage_providers_metrics') }}
    where 1 = 1
    group by 1
    order by 1
),

new_clients as (
    select
        time_bucket(interval '1 {{ period }}', first_deal_at, date '2020-10-01') as date,
        coalesce(approx_count_distinct(client_id), 0) as new_client_ids
    from {{ ref('filecoin_clients') }}
    group by 1
    order by 1 desc
),

client_metrics as (
    select
        time_bucket(interval '1 {{ period }}', date, date '2020-10-01') as date,
        count(distinct client_id) filter (where active_data_tibs > 1) as clients_with_active_data_gt_1_tibs,
    from {{ ref('filecoin_daily_clients_metrics') }}
    group by 1
    order by 1 desc
),

new_providers as (
    select
        time_bucket(interval '1 {{ period }}', first_deal_at, date '2020-10-01') as date,
        coalesce(approx_count_distinct(provider_id), 0) as new_provider_ids
    from {{ ref('filecoin_storage_providers') }}
    group by 1
    order by 1 desc
),

network_user_address_count as (
    select
        time_bucket(interval '1 {{ period }}', cast(stat_date as date), date '2020-10-01') as date,
        avg(total_address_count) as total_address_count,
        avg(active_address_count_daily) as active_address_count_daily,
        avg(active_address_count_weekly) as active_address_count_weekly,
        avg(active_address_count_monthly) as active_address_count_monthly,
        avg(total_address_count_100) as total_address_count_100,
        avg(total_address_count_1000) as total_address_count_1000,
        avg(total_address_count_10000) as total_address_count_10000,
        avg(total_address_count_100000) as total_address_count_100000,
        avg(total_address_count_1000000) as total_address_count_1000000
    from {{ source("raw_assets", "raw_network_user_address_count") }}
    group by 1
    order by 1 desc
),

gas_usage as (
    select
        time_bucket(interval '1 {{ period }}', cast(stat_date as date), date '2020-10-01') as date,
        sum(total_gas_used) * pow(10, -6) as total_gas_used_millions,
        sum(provecommit_sector_gas_used) * pow(10, -6) as provecommit_sector_gas_used_millions,
        sum(precommit_sector_gas_used) * pow(10, -6) as precommit_sector_gas_used_millions,
        sum(provecommit_aggregate_gas_used) * pow(10, -6) as provecommit_aggregate_gas_used_millions,
        sum(precommit_sector_batch_gas_used) * pow(10, -6) as precommit_sector_batch_gas_used_millions,
        sum(publish_storage_deals_gas_used) * pow(10, -6) as publish_storage_deals_gas_used_millions,
        sum(submit_windowed_post_gas_used) * pow(10, -6) as submit_windowed_post_gas_used_millions
    from {{ source("raw_assets", "raw_gas_daily_usage") }}
    group by 1
    order by 1 desc
),

direct_data_onboarding as (
    select
        time_bucket(interval '1 {{ period }}', cast(stat_date as date), date '2020-10-01') as date,
        sum(total_ddo_sector_count) as ddo_sector_onboarding_count,
        sum(total_ddo_power_tib) as ddo_sector_onboarding_raw_power_tibs
    from {{ source("raw_assets", "raw_daily_direct_data_onboarding") }}
    group by 1
    order by 1 desc
),

new_pieces as (
    select
        time_bucket(interval '1 {{ period }}', piece_first_sector_start_at, date '2020-10-01') as date,
        coalesce(approx_count_distinct(piece_cid), 0) as new_piece_cids
    from {{ ref('filecoin_state_market_deals') }}
    group by 1
    order by 1 desc
),

providers_adding_capacity as (
    with pwp as (
        select
            provider_id,
            min(date) as started_providing_power_date
        from {{ ref('filecoin_daily_storage_providers_metrics') }}
        where raw_power_pibs > 0
        group by provider_id
    )

    select
        time_bucket(interval '1 {{ period }}', started_providing_power_date, date '2020-10-01') as date,
        count(distinct provider_id) as new_providers_providing_capacity
    from pwp
    group by 1
),

circulating_supply as (
    select
        cast(stat_date as date) as date,
        circulating_fil,
        mined_fil,
        vested_fil,
        reserve_disbursed_fil,
        locked_fil,
        burnt_fil
    from {{ source("raw_assets", "raw_circulating_supply") }}
    order by date desc
),

block_rewards as (
    select
        time_bucket(interval '1 {{ period }}', cast(stat_date as date), date '2020-10-01') as date,
        avg(reward_per_wincount) as reward_per_wincount
    from {{ source("raw_assets", "raw_block_rewards") }}
    group by 1
    order by date desc
),

network_base_fee as (
    select
        time_bucket(interval '1 {{ period }}', cast(hour_date as timestamp), date '2020-10-01') as date,
        avg(unit_base_fee) as unit_base_fee
    from {{ source("raw_assets", "raw_network_base_fee") }}
    group by 1
    order by date desc
),

oso_filecoin_collection_events as (
    select
        date,
        sum(amount) filter (where event_type = 'GITHUB_repositories_daily') as github_repositories,
        sum(amount) filter (where event_type = 'GITHUB_contributors_daily') as github_contributors,
        sum(amount) filter (where event_type = 'GITHUB_comments_daily') as github_comments,
        sum(amount) filter (where event_type = 'GITHUB_stars_daily') as github_stars,
        sum(amount) filter (where event_type = 'GITHUB_forks_daily') as github_forks,
        sum(amount) filter (where event_type = 'GITHUB_releases_daily') as github_releases,
        sum(amount) filter (where event_type = 'GITHUB_commits_daily') as github_commits,
    from {{ source("raw_assets", "raw_oso_daily_filecoin_collection_events") }}
    group by date
    order by date desc
),

transactions as (
    select
        time_bucket(interval '1 {{ period }}', date, date '2020-10-01') as date,
        sum(transactions) as transactions,
        sum(total_value_fil) as total_value_fil
    from {{ source("raw_assets", "raw_filecoin_transactions") }}
    group by 1
    order by date desc
),

filecoin_daily_aggregations as (
    select
        time_bucket(interval '1 {{ period }}', date, date '2020-10-01') as date,
        sum(miner_tip_fil) as miner_tip_fil,
        sum(miner_tip_fil + burnt_fil) as miner_tips_plus_burnt_fil
    from {{ source('raw_assets', 'raw_filecoin_daily_aggregations') }}
    group by 1
    order by date desc
),

fil_price as (
    select
        time_bucket(interval '1 {{ period }}', cast(time_start as timestamp), date '2020-10-01') as date,
        avg(price_avg_usd) as fil_token_price_avg_usd,
        sum(volume_usd) as fil_token_volume_usd,
        avg(market_cap_usd) as fil_token_market_cap_usd
    from {{ source("raw_assets", "raw_fil_price") }}
    group by 1
    order by 1 desc
),

raw_goldsky_foc_metrics as (
    select
        time_bucket(interval '1 {{ period }}', cast(date as date), date '2020-10-01') as date,
        max(total_active_payers) as total_active_payers,
        max(total_usdfc_settled) as total_usdfc_settled
    from {{ source("raw_assets", "raw_goldsky_foc_metrics") }}
    group by 1
    order by 1 desc
)

select
    date_calendar.date as date,

    -- Data Onboarding
    onboarded_data_pibs,
    unique_data_onboarded_data_pibs,
    unique_data_onboarded_ratio,
    onboarded_data_pibs_with_payments,
    deal_storage_cost_fil,
    deals,
    verified_deals,
    regular_deals,
    unique_piece_cids,
    new_piece_cids,
    average_piece_replication_factor,
    data_on_active_deals_pibs,
    data_on_active_deals_pibs - lag(data_on_active_deals_pibs) over (order by date_calendar.date) as data_on_active_deals_pibs_delta,
    unique_data_on_active_deals_pibs,
    active_deals,
    active_deals - lag(active_deals) over (order by date_calendar.date) as active_deals_delta,

    -- Data Termination
    deal_ends,
    ended_data_pibs,
    deal_slashes,
    slashed_data_pibs,

    -- Users
    unique_deal_making_clients,
    unique_deal_making_providers,
    clients_with_active_deals,
    clients_with_active_deals - lag(clients_with_active_deals) over (order by date_calendar.date) as clients_with_active_deals_delta,
    providers_with_active_deals,
    providers_with_active_deals - lag(providers_with_active_deals) over (order by date_calendar.date) as providers_with_active_deals_delta,
    providers_with_power,
    mean_deal_duration_days,
    mean_verified_deal_duration_days,
    mean_regular_deal_duration_days,
    average_piece_replication_factor_active_deals,
    new_client_ids,
    new_provider_ids,
    new_providers_providing_capacity,
    active_address_count_daily,
    active_address_count_weekly,
    active_address_count_monthly,
    total_address_count,
    total_address_count_100,
    total_address_count_1000,
    total_address_count_10000,
    total_address_count_100000,
    total_address_count_1000000,
    clients_with_active_data_gt_1_tibs,

    -- Power
    raw_power_pibs,
    raw_power_pibs - lag(raw_power_pibs) over (order by date_calendar.date) as raw_power_pibs_delta,
    quality_adjusted_power_pibs,
    quality_adjusted_power_pibs - lag(quality_adjusted_power_pibs) over (order by date_calendar.date) as quality_adjusted_power_pibs_delta,
    verified_data_power_pibs,
    verified_data_power_pibs - lag(verified_data_power_pibs) over (order by date_calendar.date) as verified_data_power_pibs_delta,

    -- Storage Providers Economics
    storage_providers_balance,
    storage_providers_initial_pledge,
    storage_providers_locked_funds,
    storage_providers_pre_commit_deposits,
    storage_providers_collateral,
    storage_providers_fee_debt,
    storage_providers_blocks_mined,
    storage_providers_win_count,
    storage_providers_rewards,

    -- Others
    data_on_active_deals_pibs / raw_power_pibs as network_utilization_ratio_state_market_deals,
    verified_data_power_pibs / raw_power_pibs as network_utilization_ratio,

    -- Sector Metrics
    sector_onboarding_count,
    ddo_sector_onboarding_count,
    sector_onboarding_raw_power_pibs,
    ddo_sector_onboarding_raw_power_tibs,
    sector_onboarding_quality_adjusted_power_pibs,
    sector_terminated_raw_power_pibs,
    sector_terminated_quality_adjusted_power_pibs,
    sector_extended_raw_power_pibs,
    sector_extended_quality_adjusted_power_pibs,
    sector_fault_raw_power_pibs,
    sector_fault_quality_adjusted_power_pibs,
    sector_recover_raw_power_pibs,
    sector_recover_quality_adjusted_power_pibs,
    sector_expire_raw_power_pibs,
    sector_expire_quality_adjusted_power_pibs,
    sector_snap_raw_power_pibs,
    sector_snap_quality_adjusted_power_pibs,
    active_sector_count,

    -- Sector Events
    commit_capacity_added_events_count,
    precommit_added_events_count,
    sector_added_events_count,
    sector_extended_events_count,
    sector_faulted_events_count,
    sector_recovered_events_count,
    sector_recovering_events_count,
    sector_snapped_events_count,
    sector_terminated_events_count,

    -- Economics
    circulating_fil,
    (circulating_fil - lag(circulating_fil, {{ period_lookback }}) over (order by date_calendar.date)) as yearly_circulating_fil_delta,
    (yearly_circulating_fil_delta / lag(circulating_fil, {{ period_lookback }}) over (order by date_calendar.date) * 100) as yearly_inflation_rate,
    mined_fil,
    vested_fil,
    reserve_disbursed_fil,
    locked_fil,
    burnt_fil,
    miner_tips_plus_burnt_fil,
    miner_tip_fil,
    reward_per_wincount,

    -- Fil Plus Shares
    (quality_adjusted_power_pibs - raw_power_pibs) / (9 * raw_power_pibs) as fil_plus_bytes_share,
    10 * (quality_adjusted_power_pibs - raw_power_pibs)/ (9 * quality_adjusted_power_pibs) as fil_plus_rewards_share,

    -- Gas Usage
    total_gas_used_millions,
    unit_base_fee,
    provecommit_sector_gas_used_millions,
    precommit_sector_gas_used_millions,
    provecommit_aggregate_gas_used_millions,
    precommit_sector_batch_gas_used_millions,
    publish_storage_deals_gas_used_millions,
    submit_windowed_post_gas_used_millions,

    -- Oso Filecoin Collection Events
    github_repositories,
    github_contributors,
    github_comments,
    github_stars,
    github_forks,
    github_releases,
    github_commits,

    -- Transactions
    transactions,
    total_value_fil,

    -- FIL Price (USD)
    fil_token_price_avg_usd,
    fil_token_volume_usd,
    fil_token_market_cap_usd,

    -- FOC
    total_active_payers,
    total_usdfc_settled

from date_calendar
left join deal_metrics on date_calendar.date = deal_metrics.date
left join users_with_active_deals on date_calendar.date = users_with_active_deals.date
left join deal_ends on date_calendar.date = deal_ends.date
left join deal_slashes on date_calendar.date = deal_slashes.date
left join provider_metrics on date_calendar.date = provider_metrics.date
left join new_clients on date_calendar.date = new_clients.date
left join client_metrics on date_calendar.date = client_metrics.date
left join new_providers on date_calendar.date = new_providers.date
left join network_user_address_count on date_calendar.date = network_user_address_count.date
left join direct_data_onboarding on date_calendar.date = direct_data_onboarding.date
left join new_pieces on date_calendar.date = new_pieces.date
left join providers_adding_capacity on date_calendar.date = providers_adding_capacity.date
left join circulating_supply on date_calendar.date = circulating_supply.date
left join block_rewards on date_calendar.date = block_rewards.date
left join network_base_fee on date_calendar.date = network_base_fee.date
left join gas_usage on date_calendar.date = gas_usage.date
left join oso_filecoin_collection_events on date_calendar.date = oso_filecoin_collection_events.date
left join transactions on date_calendar.date = transactions.date
left join filecoin_daily_aggregations on date_calendar.date = filecoin_daily_aggregations.date
left join fil_price on date_calendar.date = fil_price.date
left join raw_goldsky_foc_metrics on date_calendar.date = raw_goldsky_foc_metrics.date
order by date_calendar.date desc

{% endmacro %}
