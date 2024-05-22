with date_calendar as (
  select
    cast(range as date) as date
  from range(date '2020-09-12', current_date() - interval '2 day', interval '1 day')
),

deal_metrics as (
    select
        cast(sector_start_at as date) as date,
        provider_id,
        sum(padded_piece_size_tibs) as onboarded_data_tibs,
        count(distinct deal_id) as deals,
        count(distinct piece_cid) as unique_piece_cids,
        count(distinct client_id) as unique_deal_making_clients,
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
        quality_adj_power as quality_adjusted_power_bytes,
        quality_adj_power / 1024 ^ 5 as quality_adjusted_power_pibs,
        (quality_adjusted_power_bytes - raw_power_bytes) / 9 as verified_data_power_bytes,
        (quality_adjusted_power_pibs - raw_power_pibs) / 9 as verified_data_power_pibs,
    from {{ source('raw_assets', 'raw_storage_providers_daily_power') }}
    where date is not null and provider_id is not null
),

token_balance_data as (
    select
        stat_date::date as date,
        miner_id as provider_id,
        balance,
        initial_pledge,
        locked_funds,
        pre_commit_deposits,
        provider_collateral,
        fee_debt
    from {{ source("raw_assets", "raw_storage_providers_token_balances") }}
    where date is not null and provider_id is not null
),

sector_totals as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        total_num_sector,
        daily_sector_onboarding_count - lag(daily_sector_onboarding_count) over (partition by provider_id order by date) as daily_sector_onboarding_count,
        total_sector_rbp / 1024 ^ 4 as total_sector_raw_power_tibs,
        total_sector_qap / 1024 ^ 4 as total_sector_quality_adjusted_power_tibs,
        daily_sector_onboarding_rbp / 1024 ^ 4 as daily_sector_onboarding_raw_power_tibs,
        daily_sector_onboarding_qap / 1024 ^ 4 as daily_sector_onboarding_quality_adjusted_power_tibs,
    from {{ source("raw_assets", "raw_storage_providers_sector_totals") }}
    where date is not null and provider_id is not null
),

sector_commits_count as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        total_sealed_sector_count,
        precommit_sector_count,
        precommit_batch_sector_count,
        avg_precommit_batch_sector_count,
        provecommit_sector_count,
        provecommit_batch_sector_count,
        avg_provecommit_batch_sector_count
    from {{ source("raw_assets", "raw_storage_providers_sector_commits_count") }}
    where date is not null and provider_id is not null
),

sector_commits_size as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        precommit_sector_rbp / 1024 ^ 4 as precommit_sector_raw_power_tibs,
        precommit_sector_qap / 1024 ^ 4 as precommit_sector_quality_adjusted_power_tibs,
        precommit_batch_sector_rbp / 1024 ^ 4 as precommit_batch_sector_raw_power_tibs,
        precommit_batch_sector_qap / 1024 ^ 4 as precommit_batch_sector_quality_adjusted_power_tibs,
        provecommit_sector_rbp / 1024 ^ 4 as provecommit_sector_raw_power_tibs,
        provecommit_sector_qap / 1024 ^ 4 as provecommit_sector_quality_adjusted_power_tibs,
        provecommit_batch_sector_rbp / 1024 ^ 4 as provecommit_batch_sector_raw_power_tibs,
    from {{ source("raw_assets", "raw_storage_providers_sector_commits_size") }}
    where date is not null and provider_id is not null
),

sector_terminations as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        daily_new_terminate_rbp / 1024 ^ 4 as daily_new_terminated_raw_power_tibs,
        daily_new_terminate_qap / 1024 ^ 4 as daily_new_terminated_quality_adjusted_power_tibs,
        total_terminate_rbp / 1024 ^ 4 as total_terminated_raw_power_tibs,
        total_terminate_qap / 1024 ^ 4 as total_terminated_quality_adjusted_power_tibs,
        daily_new_active_terminate_rbp / 1024 ^ 4 as daily_new_active_terminated_raw_power_tibs,
        daily_new_active_terminate_qap / 1024 ^ 4 as daily_new_active_terminated_quality_adjusted_power_tibs,
        total_active_terminate_rbp / 1024 ^ 4 as total_active_terminated_raw_power_tibs,
        total_active_terminate_qap / 1024 ^ 4 as total_active_terminated_quality_adjusted_power_tibs,
        daily_new_passive_terminate_rbp / 1024 ^ 4 as daily_new_passive_terminated_raw_power_tibs,
        daily_new_passive_terminate_qap / 1024 ^ 4 as daily_new_passive_terminated_quality_adjusted_power_tibs,
        total_passive_terminate_rbp / 1024 ^ 4 as total_passive_terminated_raw_power_tibs,
        total_passive_terminate_qap / 1024 ^ 4 as total_passive_terminated_quality_adjusted_power_tibs
    from {{ source("raw_assets", "raw_storage_providers_sector_terminations") }}
    where date is not null and provider_id is not null
),

sector_faults as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        daily_new_fault_rbp / 1024 ^ 4 as daily_new_fault_raw_power_tibs,
        daily_new_fault_qap / 1024 ^ 4 as daily_new_fault_quality_adjusted_power_tibs,
        active_fault_rbp / 1024 ^ 4 as active_fault_raw_power_tibs,
        active_fault_qap / 1024 ^ 4 as active_fault_quality_adjusted_power_tibs,
    from {{ source("raw_assets", "raw_storage_providers_sector_faults") }}
    where date is not null and provider_id is not null
),

sector_recoveries as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        daily_new_recover_rbp / 1024 ^ 4 as daily_new_recover_raw_power_tibs,
        daily_new_recover_qap / 1024 ^ 4 as daily_new_recover_quality_adjusted_power_tibs,
    from {{ source("raw_assets", "raw_storage_providers_sector_recoveries") }}
),

sector_expirations as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        daily_new_expire_rbp / 1024 ^ 4 as daily_new_expire_raw_power_tibs,
        daily_new_expire_qap / 1024 ^ 4 as daily_new_expire_quality_adjusted_power_tibs,
        total_expire_rbp / 1024 ^ 4 as total_expire_raw_power_tibs,
        total_expire_qap / 1024 ^ 4 as total_expire_quality_adjusted_power_tibs
    from {{ source("raw_assets", "raw_storage_providers_sector_expirations") }}
),

sector_extensions as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        daily_new_extend_rbp / 1024 ^ 4 as daily_new_extend_raw_power_tibs,
        daily_new_extend_qap / 1024 ^ 4 as daily_new_extend_quality_adjusted_power_tibs
    from {{ source("raw_assets", "raw_storage_providers_sector_extensions") }}
),

sector_snaps as (
    select
        stat_date::date as date,
        trim(miner_id) as provider_id,
        daily_new_snap_rbp / 1024 ^ 4 as daily_new_snap_raw_power_tibs,
        daily_new_snap_qap / 1024 ^ 4 as daily_new_snap_quality_adjusted_power_tibs,
        total_snap_rbp / 1024 ^ 4 as total_snap_raw_power_tibs,
        total_snap_qap / 1024 ^ 4 as total_snap_quality_adjusted_power_tibs
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
        success_rate as spark_retrieval_success_rate
    from {{ source("raw_assets", "raw_spark_retrieval_success_rate") }}
),

rewards_data as (
    select
        stat_date::date as date,
        miner_id as provider_id,
        blocks_mined as total_blocks_mined,
        win_count as total_win_count,
        rewards as total_rewards,
        lag(total_rewards) over (partition by miner_id order by date) as rewards,
        lag(total_blocks_mined) over (partition by miner_id order by date) as blocks_mined,
        lag(total_win_count) over (partition by miner_id order by date) as win_count,
    from {{ source("raw_assets", "raw_storage_providers_rewards") }}
    where date is not null and provider_id is not null
)

select
    dc.date,
    coalesce(dm.provider_id, spp.provider_id, tbd.provider_id, rd.provider_id) as provider_id,
    coalesce(dm.onboarded_data_tibs, 0) as onboarded_data_tibs,
    coalesce(dm.deals, 0) as deals,
    coalesce(dm.unique_piece_cids, 0) as unique_piece_cids,
    coalesce(dm.unique_deal_making_clients, 0) as unique_deal_making_clients,
    spp.raw_power_bytes,
    spp.raw_power_pibs,
    spp.quality_adjusted_power_bytes,
    spp.quality_adjusted_power_pibs,
    spp.verified_data_power_bytes,
    spp.verified_data_power_pibs,
    tbd.balance,
    tbd.initial_pledge,
    tbd.locked_funds,
    tbd.pre_commit_deposits,
    tbd.provider_collateral,
    tbd.fee_debt,
    st.total_num_sector,
    st.daily_sector_onboarding_count,
    st.total_sector_raw_power_tibs,
    st.total_sector_quality_adjusted_power_tibs,
    st.daily_sector_onboarding_raw_power_tibs,
    st.daily_sector_onboarding_quality_adjusted_power_tibs,
    scc.total_sealed_sector_count,
    scc.precommit_sector_count,
    scc.precommit_batch_sector_count,
    scc.avg_precommit_batch_sector_count,
    scc.provecommit_sector_count,
    scc.provecommit_batch_sector_count,
    scc.avg_provecommit_batch_sector_count,
    scs.precommit_sector_raw_power_tibs,
    scs.precommit_sector_quality_adjusted_power_tibs,
    scs.precommit_batch_sector_raw_power_tibs,
    scs.precommit_batch_sector_quality_adjusted_power_tibs,
    scs.provecommit_sector_raw_power_tibs,
    scs.provecommit_sector_quality_adjusted_power_tibs,
    scs.provecommit_batch_sector_raw_power_tibs,
    sterm.daily_new_terminated_raw_power_tibs,
    sterm.daily_new_terminated_quality_adjusted_power_tibs,
    sterm.total_terminated_raw_power_tibs,
    sterm.total_terminated_quality_adjusted_power_tibs,
    sterm.daily_new_active_terminated_raw_power_tibs,
    sterm.daily_new_active_terminated_quality_adjusted_power_tibs,
    sterm.total_active_terminated_raw_power_tibs,
    sterm.total_active_terminated_quality_adjusted_power_tibs,
    sterm.daily_new_passive_terminated_raw_power_tibs,
    sterm.daily_new_passive_terminated_quality_adjusted_power_tibs,
    sterm.total_passive_terminated_raw_power_tibs,
    sterm.total_passive_terminated_quality_adjusted_power_tibs,
    sf.daily_new_fault_raw_power_tibs,
    sf.daily_new_fault_quality_adjusted_power_tibs,
    sf.active_fault_raw_power_tibs,
    sf.active_fault_quality_adjusted_power_tibs,
    sr.daily_new_recover_raw_power_tibs,
    sr.daily_new_recover_quality_adjusted_power_tibs,
    sexp.daily_new_expire_raw_power_tibs,
    sexp.daily_new_expire_quality_adjusted_power_tibs,
    sexp.total_expire_raw_power_tibs,
    sexp.total_expire_quality_adjusted_power_tibs,
    sext.daily_new_extend_raw_power_tibs,
    sext.daily_new_extend_quality_adjusted_power_tibs,
    ss.daily_new_snap_raw_power_tibs,
    ss.daily_new_snap_quality_adjusted_power_tibs,
    ss.total_snap_raw_power_tibs,
    ss.total_snap_quality_adjusted_power_tibs,
    rd.blocks_mined,
    rd.win_count,
    rd.rewards,
    rd.total_blocks_mined,
    rd.total_win_count,
    rd.total_rewards,
    sd.avg_active_sector_duration_days,
    sd.std_active_sector_duration_days,
    spark.spark_retrieval_success_rate,
from date_calendar dc
full outer join storage_providers_power spp on dc.date = spp.date
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
where dc.date >= '2020-09-12'
order by dc.date desc
