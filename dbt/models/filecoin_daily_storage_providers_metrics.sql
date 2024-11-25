with date_calendar as (
  select
    cast(range as date) as date
  from range(date '2020-09-12', current_date(), interval '1 day')
),

deal_metrics as (
    select
        cast(sector_start_at as date) as date,
        provider_id,
        sum(padded_piece_size_tibs) as onboarded_data_tibs,
        approx_count_distinct(deal_id) as deals,
        approx_count_distinct(piece_cid) as unique_piece_cids,
        approx_count_distinct(client_id) as unique_deal_making_clients,
    from {{ ref('filecoin_state_market_deals') }}
    where 1 = 1
        and sector_start_at is not null
        and provider_id is not null
    group by 1, 2
),

storage_providers_power as (
    select
        stat_date::date as date,
        miner_id as provider_id,
        raw_byte_power as raw_power_bytes,
        raw_byte_power / 1024 ^ 5 as raw_power_pibs,
        avg(raw_power_pibs) over provider_last_30 as lagging_30_days_avg_raw_power_pibs,
        quality_adj_power as quality_adjusted_power_bytes,
        quality_adj_power / 1024 ^ 5 as quality_adjusted_power_pibs,
        avg(quality_adjusted_power_pibs) over provider_last_30 as lagging_30_days_avg_quality_adjusted_power_pibs,
        (quality_adjusted_power_bytes - raw_power_bytes) / 9 as verified_data_power_bytes,
        (quality_adjusted_power_pibs - raw_power_pibs) / 9 as verified_data_power_pibs,
        avg(verified_data_power_pibs) over provider_last_30 as lagging_30_days_avg_verified_data_power_pibs,
        cast(round((raw_byte_power / 1024 ^ 3) / spi.sector_size_gibs, 0) as int) as active_sectors
    from {{ source('raw_assets', 'raw_storage_providers_daily_power') }} as spdp
    left join {{ source("raw_assets", "raw_filecoin_storage_providers_information") }} as spi on spdp.miner_id = spi.provider_id
    where spdp.stat_date is not null and spdp.miner_id is not null
    window provider_last_30 as (partition by provider_id order by date rows between 29 preceding and current row)
),

storage_providers_power_growth as (
    select
        date,
        provider_id,
        lagging_30_days_avg_raw_power_pibs - lag(lagging_30_days_avg_raw_power_pibs) over providers as smoothed_raw_power_growth_pibs,
        lagging_30_days_avg_quality_adjusted_power_pibs - lag(lagging_30_days_avg_quality_adjusted_power_pibs) over providers as smoothed_quality_adjusted_power_growth_pibs,
        lagging_30_days_avg_verified_data_power_pibs - lag(lagging_30_days_avg_verified_data_power_pibs) over providers as smoothed_verified_data_power_growth_pibs
    from storage_providers_power
    window providers as (partition by provider_id order by date)
),

token_balance_data as (
    select
        stat_date::date as date,
        miner_id as provider_id,
        balance,
        balance - lag(balance) over (partition by provider_id order by date) as balance_change,
        initial_pledge,
        initial_pledge - lag(initial_pledge) over (partition by provider_id order by date) as initial_pledge_change,
        locked_funds,
        locked_funds - lag(locked_funds) over (partition by provider_id order by date) as locked_funds_change,
        pre_commit_deposits,
        provider_collateral,
        provider_collateral - lag(provider_collateral) over (partition by provider_id order by date) as provider_collateral_change,
        fee_debt
    from {{ source("raw_assets", "raw_storage_providers_token_balances") }}
    where date is not null and provider_id is not null
),

sector_totals as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        total_num_sector as daily_sector_onboarding_count,
        total_sector_rbp / 1024 ^ 4 as daily_sector_onboarding_raw_power_tibs,
        total_sector_qap / 1024 ^ 4 as daily_sector_onboarding_quality_adjusted_power_tibs,
        daily_sector_onboarding_count as total_sector_onboarded_count,
        daily_sector_onboarding_rbp / 1024 ^ 4 as total_sector_onboarding_raw_power_tibs,
        daily_sector_onboarding_qap / 1024 ^ 4 as total_sector_onboarding_quality_adjusted_power_tibs,
    from {{ source("raw_assets", "raw_storage_providers_sector_totals") }}
    where date is not null and provider_id is not null
),

sector_commits_count as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        total_sealed_sector_count,
        precommit_sector_count as total_precommit_sector_count,
        precommit_batch_sector_count as total_precommit_batch_sector_count,
        avg_precommit_batch_sector_count,
        provecommit_sector_count as total_provecommit_sector_count,
        provecommit_batch_sector_count as total_provecommit_batch_sector_count,
        avg_provecommit_batch_sector_count
    from {{ source("raw_assets", "raw_storage_providers_sector_commits_count") }}
    where date is not null and provider_id is not null
),

sector_commits_size as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        precommit_sector_rbp / 1024 ^ 4 as total_precommit_sector_raw_power_tibs,
        precommit_sector_qap / 1024 ^ 4 as total_precommit_sector_quality_adjusted_power_tibs,
        precommit_batch_sector_rbp / 1024 ^ 4 as total_precommit_batch_sector_raw_power_tibs,
        precommit_batch_sector_qap / 1024 ^ 4 as total_precommit_batch_sector_quality_adjusted_power_tibs,
        provecommit_sector_rbp / 1024 ^ 4 as total_provecommit_sector_raw_power_tibs,
        provecommit_sector_qap / 1024 ^ 4 as total_provecommit_sector_quality_adjusted_power_tibs,
        provecommit_batch_sector_rbp / 1024 ^ 4 as total_provecommit_batch_sector_raw_power_tibs,
    from {{ source("raw_assets", "raw_storage_providers_sector_commits_size") }}
    where date is not null and provider_id is not null
),

sector_terminations as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        daily_new_terminate_rbp / 1024 ^ 4 as daily_new_sector_terminated_raw_power_tibs,
        daily_new_terminate_qap / 1024 ^ 4 as daily_new_sector_terminated_quality_adjusted_power_tibs,
        total_terminate_rbp / 1024 ^ 4 as total_sector_terminated_raw_power_tibs,
        total_terminate_qap / 1024 ^ 4 as total_sector_terminated_quality_adjusted_power_tibs,
        daily_new_active_terminate_rbp / 1024 ^ 4 as daily_new_sector_active_terminated_raw_power_tibs,
        daily_new_active_terminate_qap / 1024 ^ 4 as daily_new_sector_active_terminated_quality_adjusted_power_tibs,
        total_active_terminate_rbp / 1024 ^ 4 as total_sector_active_terminated_raw_power_tibs,
        total_active_terminate_qap / 1024 ^ 4 as total_sector_active_terminated_quality_adjusted_power_tibs,
        daily_new_passive_terminate_rbp / 1024 ^ 4 as daily_new_sector_passive_terminated_raw_power_tibs,
        daily_new_passive_terminate_qap / 1024 ^ 4 as daily_new_sector_passive_terminated_quality_adjusted_power_tibs,
        total_passive_terminate_rbp / 1024 ^ 4 as total_sector_passive_terminated_raw_power_tibs,
        total_passive_terminate_qap / 1024 ^ 4 as total_sector_passive_terminated_quality_adjusted_power_tibs
    from {{ source("raw_assets", "raw_storage_providers_sector_terminations") }}
    where date is not null and provider_id is not null
),

sector_faults as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        daily_new_fault_rbp / 1024 ^ 4 as daily_new_sector_fault_raw_power_tibs,
        daily_new_fault_qap / 1024 ^ 4 as daily_new_sector_fault_quality_adjusted_power_tibs,
        active_fault_rbp / 1024 ^ 4 as active_sector_fault_raw_power_tibs,
        active_fault_qap / 1024 ^ 4 as active_sector_fault_quality_adjusted_power_tibs,
    from {{ source("raw_assets", "raw_storage_providers_sector_faults") }}
    where date is not null and provider_id is not null
),

sector_recoveries as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        daily_new_recover_rbp / 1024 ^ 4 as daily_new_sector_recover_raw_power_tibs,
        daily_new_recover_qap / 1024 ^ 4 as daily_new_sector_recover_quality_adjusted_power_tibs,
    from {{ source("raw_assets", "raw_storage_providers_sector_recoveries") }}
),

sector_expirations as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        daily_new_expire_rbp / 1024 ^ 4 as daily_new_sector_expire_raw_power_tibs,
        daily_new_expire_qap / 1024 ^ 4 as daily_new_sector_expire_quality_adjusted_power_tibs,
        total_expire_rbp / 1024 ^ 4 as total_sector_expire_raw_power_tibs,
        total_expire_qap / 1024 ^ 4 as total_sector_expire_quality_adjusted_power_tibs
    from {{ source("raw_assets", "raw_storage_providers_sector_expirations") }}
),

sector_extensions as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        daily_new_extend_rbp / 1024 ^ 4 as daily_new_sector_extend_raw_power_tibs,
        daily_new_extend_qap / 1024 ^ 4 as daily_new_sector_extend_quality_adjusted_power_tibs
    from {{ source("raw_assets", "raw_storage_providers_sector_extensions") }}
),

sector_snaps as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        daily_new_snap_rbp / 1024 ^ 4 as daily_new_sector_snap_raw_power_tibs,
        daily_new_snap_qap / 1024 ^ 4 as daily_new_sector_snap_quality_adjusted_power_tibs,
        total_snap_rbp / 1024 ^ 4 as total_sector_snap_raw_power_tibs,
        total_snap_qap / 1024 ^ 4 as total_sector_snap_quality_adjusted_power_tibs
    from {{ source("raw_assets", "raw_storage_providers_sector_snaps") }}
),

sector_durations as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        avg_active_sector_duration_days,
        std_active_sector_duration_days
    from {{ source("raw_assets", "raw_storage_providers_sector_durations") }}
),

spark_retrievals as (
    select
        date,
        provider_id,
        total_retrieval_requests,
        successful_retrieval_requests,
        spark_retrieval_success_rate
    from {{ ref('filecoin_spark_retrievals') }}
),

rewards_data as (
    select
        stat_date::date as date,
        miner_id as provider_id,
        blocks_mined as total_blocks_mined,
        win_count as total_win_count,
        rewards as total_rewards,
        total_rewards - lag(total_rewards) over (partition by miner_id order by date) as daily_rewards,
        total_blocks_mined - lag(total_blocks_mined) over (partition by miner_id order by date) as daily_blocks_mined,
        total_win_count - lag(total_win_count) over (partition by miner_id order by date) as daily_win_count,
    from {{ source("raw_assets", "raw_storage_providers_rewards") }}
    where date is not null and provider_id is not null
),

deal_count as (
    select
        stat_date::date as date,
        miner_id as provider_id,
        total_regular_deal_count,
        total_verified_deal_count,
        daily_new_regular_deal_count,
        daily_new_verified_deal_count,
        active_regular_deal_count,
        active_verified_deal_count,
        total_regular_deal_free_count,
        total_verified_deal_free_count
    from {{ source("raw_assets", "raw_storage_providers_deal_count") }}
    where date is not null and provider_id is not null
),

deal_duration as (
    select
        stat_date::date as date,
        miner_id as provider_id,
        avg_regular_deal_duration_days,
        avg_verified_deal_duration_days
    from {{ source("raw_assets", "raw_storage_providers_deal_duration") }}
    where date is not null and provider_id is not null
),

deal_revenue as (
    select
        stat_date::date as date,
        miner_id as provider_id,
        total_regular_deal_revenue,
        total_verified_deal_revenue
    from {{ source("raw_assets", "raw_storage_providers_deal_revenue") }}
    where date is not null and provider_id is not null
),

sector_events as (
    pivot {{ source("raw_assets", "raw_daily_providers_sector_events") }}
    on concat(lower(event), '_events_count')
    using sum(count)
)

select
    dc.date,
    coalesce(dm.provider_id, spp.provider_id, tbd.provider_id, rd.provider_id) as provider_id,

    -- Deal Metrics
    coalesce(dm.onboarded_data_tibs, 0) as onboarded_data_tibs,
    coalesce(dm.deals, 0) as deals,
    coalesce(dm.unique_piece_cids, 0) as unique_piece_cids,
    coalesce(dm.unique_deal_making_clients, 0) as unique_deal_making_clients,

    -- Power Metrics
    spp.raw_power_bytes,
    spp.raw_power_pibs,
    spp.lagging_30_days_avg_raw_power_pibs,
    spp.quality_adjusted_power_bytes,
    spp.quality_adjusted_power_pibs,
    spp.lagging_30_days_avg_quality_adjusted_power_pibs,
    spp.verified_data_power_bytes,
    spp.verified_data_power_pibs,
    spp.lagging_30_days_avg_verified_data_power_pibs,
    spg.smoothed_raw_power_growth_pibs,
    spg.smoothed_quality_adjusted_power_growth_pibs,
    spg.smoothed_verified_data_power_growth_pibs,

    -- Active Sectors
    spp.active_sectors,

    -- Token Metrics
    tbd.balance,
    tbd.initial_pledge,
    tbd.locked_funds,
    tbd.pre_commit_deposits,
    tbd.provider_collateral,
    tbd.fee_debt,

    -- Sector Metrics
    st.daily_sector_onboarding_count,
    st.daily_sector_onboarding_raw_power_tibs,
    st.daily_sector_onboarding_quality_adjusted_power_tibs,
    st.total_sector_onboarded_count,
    st.total_sector_onboarding_raw_power_tibs,
    st.total_sector_onboarding_quality_adjusted_power_tibs,
    scc.total_sealed_sector_count,
    scc.total_precommit_sector_count,
    scc.total_precommit_batch_sector_count,
    scc.avg_precommit_batch_sector_count,
    scc.total_provecommit_sector_count,
    scc.total_provecommit_batch_sector_count,
    scc.avg_provecommit_batch_sector_count,
    scs.total_precommit_sector_raw_power_tibs,
    scs.total_precommit_sector_quality_adjusted_power_tibs,
    scs.total_precommit_batch_sector_raw_power_tibs,
    scs.total_precommit_batch_sector_quality_adjusted_power_tibs,
    scs.total_provecommit_sector_raw_power_tibs,
    scs.total_provecommit_sector_quality_adjusted_power_tibs,
    scs.total_provecommit_batch_sector_raw_power_tibs,
    sterm.daily_new_sector_terminated_raw_power_tibs,
    sterm.daily_new_sector_terminated_quality_adjusted_power_tibs,
    sterm.total_sector_terminated_raw_power_tibs,
    sterm.total_sector_terminated_quality_adjusted_power_tibs,
    sterm.daily_new_sector_active_terminated_raw_power_tibs,
    sterm.daily_new_sector_active_terminated_quality_adjusted_power_tibs,
    sterm.total_sector_active_terminated_raw_power_tibs,
    sterm.total_sector_active_terminated_quality_adjusted_power_tibs,
    sterm.daily_new_sector_passive_terminated_raw_power_tibs,
    sterm.daily_new_sector_passive_terminated_quality_adjusted_power_tibs,
    sterm.total_sector_passive_terminated_raw_power_tibs,
    sterm.total_sector_passive_terminated_quality_adjusted_power_tibs,
    sf.daily_new_sector_fault_raw_power_tibs,
    sf.daily_new_sector_fault_quality_adjusted_power_tibs,
    sf.active_sector_fault_raw_power_tibs,
    sf.active_sector_fault_quality_adjusted_power_tibs,
    sr.daily_new_sector_recover_raw_power_tibs,
    sr.daily_new_sector_recover_quality_adjusted_power_tibs,
    sexp.daily_new_sector_expire_raw_power_tibs,
    sexp.daily_new_sector_expire_quality_adjusted_power_tibs,
    sexp.total_sector_expire_raw_power_tibs,
    sexp.total_sector_expire_quality_adjusted_power_tibs,
    sext.daily_new_sector_extend_raw_power_tibs,
    sext.daily_new_sector_extend_quality_adjusted_power_tibs,
    ss.daily_new_sector_snap_raw_power_tibs,
    ss.daily_new_sector_snap_quality_adjusted_power_tibs,
    ss.total_sector_snap_raw_power_tibs,
    ss.total_sector_snap_quality_adjusted_power_tibs,
    sd.avg_active_sector_duration_days,
    sd.std_active_sector_duration_days,

    -- Rewards Metrics
    rd.daily_blocks_mined,
    rd.daily_win_count,
    rd.daily_rewards,
    rd.total_blocks_mined,
    rd.total_win_count,
    rd.total_rewards,

    -- Retrieval Metrics
    spark.spark_retrieval_success_rate,
    spark.total_retrieval_requests,
    spark.successful_retrieval_requests,

    -- Deal Metrics
    dec.total_regular_deal_count,
    dec.total_verified_deal_count,
    dec.daily_new_regular_deal_count,
    dec.daily_new_verified_deal_count,
    dec.active_regular_deal_count,
    dec.active_verified_deal_count,
    dec.total_regular_deal_free_count,
    dec.total_verified_deal_free_count,
    ded.avg_regular_deal_duration_days,
    ded.avg_verified_deal_duration_days,
    der.total_regular_deal_revenue,
    der.total_verified_deal_revenue,

    -- Sector Events
    se.commit_capacity_added_events_count,
    se.precommit_added_events_count,
    se.sector_added_events_count,
    se.sector_extended_events_count,
    se.sector_faulted_events_count,
    se.sector_recovered_events_count,
    se.sector_recovering_events_count,
    se.sector_snapped_events_count,
    se.sector_terminated_events_count
from date_calendar dc
full outer join storage_providers_power spp on dc.date = spp.date
full outer join storage_providers_power_growth spg on dc.date = spg.date and spp.provider_id = spg.provider_id
full outer join deal_metrics dm on dc.date = dm.date and spp.provider_id = dm.provider_id
full outer join token_balance_data tbd on dc.date = tbd.date and spp.provider_id = tbd.provider_id
full outer join sector_totals st on dc.date = st.date and spp.provider_id = st.provider_id
full outer join sector_commits_count scc on dc.date = scc.date and spp.provider_id = scc.provider_id
full outer join sector_commits_size scs on dc.date = scs.date and spp.provider_id = scs.provider_id
full outer join sector_terminations sterm on dc.date = sterm.date and spp.provider_id = sterm.provider_id
full outer join sector_faults sf on dc.date = sf.date and spp.provider_id = sf.provider_id
full outer join sector_recoveries sr on dc.date = sr.date and spp.provider_id = sr.provider_id
full outer join sector_expirations sexp on dc.date = sexp.date and spp.provider_id = sexp.provider_id
full outer join sector_extensions sext on dc.date = sext.date and spp.provider_id = sext.provider_id
full outer join sector_snaps ss on dc.date = ss.date and spp.provider_id = ss.provider_id
full outer join sector_durations sd on dc.date = sd.date and spp.provider_id = sd.provider_id
full outer join rewards_data rd on dc.date = rd.date and spp.provider_id = rd.provider_id
full outer join spark_retrievals spark on dc.date = spark.date and spp.provider_id = spark.provider_id
full outer join deal_count dec on dc.date = dec.date and spp.provider_id = dec.provider_id
full outer join deal_duration ded on dc.date = ded.date and spp.provider_id = ded.provider_id
full outer join deal_revenue der on dc.date = der.date and spp.provider_id = der.provider_id
full outer join sector_events se on dc.date = se.date and spp.provider_id = se.provider_id
where 1=1
    and dc.date >= '2020-09-12'
    and (
        dm.provider_id is not null
        or spp.provider_id is not null
        or tbd.provider_id is not null
        or rd.provider_id is not null
    )
order by dc.date desc
