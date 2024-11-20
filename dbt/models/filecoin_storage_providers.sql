with base_providers as (
    select
        distinct provider_id
    from {{ ref("filecoin_daily_storage_providers_metrics") }}
    where provider_id is not null
    union
    select
        distinct provider_id
    from {{ ref("filecoin_state_market_deals") }}
    where provider_id is not null
    union
    select
        distinct trim(miner_id) as provider_id
    from {{ source("raw_assets", "raw_storage_providers_token_balances") }}
    where provider_id is not null
    union
    select distinct
        trim(provider_id) as provider_id
    from {{ ref('filecoin_spark_retrievals') }}
    where provider_id is not null
),

storage_provider_location as (
    select * from {{ ref("filecoin_storage_providers_location") }}
),

stats as (
    select
        provider_id,
        count(distinct deal_id) as total_deals,
        count(distinct deal_id) filter (where is_verified) as total_verified_deals,
        count(distinct deal_id) filter (where is_active) as total_active_deals,
        count(distinct deal_id) filter (where slash_at is not null) as total_slashed_deals,
        count(distinct deal_id) filter (where not is_active) as total_finished_deals,
        count(distinct deal_id) filter (where is_active and is_verified) as total_active_verified_deals,

        count(distinct piece_cid) as total_unique_piece_cids,
        count(distinct piece_cid) filter (where is_verified) as total_verified_unique_piece_cids,
        count(distinct piece_cid) filter (where is_active) as total_active_unique_piece_cids,
        count(distinct piece_cid) filter (where is_active and is_verified) as total_active_verified_unique_piece_cids,

        sum(unpadded_piece_size_tibs) as total_data_uploaded_tibs,
        sum(unpadded_piece_size_tibs) filter (where is_active) as total_active_data_uploaded_tibs,
        sum(unpadded_piece_size_tibs) filter (piece_provider_replication_order = 1) as unique_data_uploaded_tibs,
        sum(unpadded_piece_size_tibs) filter (where is_active and piece_provider_replication_order = 1) as unique_active_data_uploaded_tibs,
        unique_data_uploaded_tibs / sum(unpadded_piece_size_tibs) as unique_data_uploaded_ratio,

        count(distinct client_id) as total_unique_clients,
        count(distinct client_id) filter (where is_active) as total_active_unique_clients,
        count(distinct client_id) filter (where is_active and is_verified) as total_active_verified_unique_clients,

        min(sector_start_at) as first_deal_at,
        min(case when is_active then sector_start_at else null end) as first_active_deal_at,
        max(sector_start_at) as last_deal_at,
        max(case when is_active then sector_start_at else null end) as last_active_deal_at,

        max(end_at) as last_deal_end_at,
        max(slash_at) as last_deal_slash_at,

        sum(unpadded_piece_size_tibs) filter(where sector_start_at > current_date() - interval '30 days') as data_uploaded_tibs_30d,
        sum(unpadded_piece_size_tibs) filter(where sector_start_at > current_date() - interval '6 months') as data_uploaded_tibs_6m,
        sum(unpadded_piece_size_tibs) filter(where sector_start_at > current_date() - interval '1 year') as data_uploaded_tibs_1y,
    from {{ ref("filecoin_state_market_deals") }}
    where sector_start_epoch is not null
    group by 1
),

reputation_data as (
    select
        address as provider_id,
        if(reachability = 'reachable', true, false) as is_reachable,
        name as provider_name,
        uptimeaverage as filrep_uptime_average,
        score as filrep_score,
        rank as filrep_rank
    from {{ source('raw_assets', 'raw_storage_providers_filrep_reputation') }}
    qualify row_number() over (partition by address order by name desc) = 1
),

latest_sp_data as (
    select distinct
        provider_id,
        raw_power_pibs,
        quality_adjusted_power_pibs,
        verified_data_power_pibs,
        balance,
        initial_pledge,
        locked_funds,
        pre_commit_deposits,
        provider_collateral,
        fee_debt,
        daily_sector_onboarding_count,
        daily_sector_onboarding_raw_power_tibs,
        daily_sector_onboarding_quality_adjusted_power_tibs,
        total_sector_onboarded_count,
        total_sector_onboarding_raw_power_tibs,
        total_sector_onboarding_quality_adjusted_power_tibs,
        total_sealed_sector_count,
        total_precommit_sector_count,
        total_precommit_batch_sector_count,
        avg_precommit_batch_sector_count,
        total_provecommit_sector_count,
        total_provecommit_batch_sector_count,
        avg_provecommit_batch_sector_count,
        total_precommit_sector_raw_power_tibs,
        total_precommit_sector_quality_adjusted_power_tibs,
        total_precommit_batch_sector_raw_power_tibs,
        total_precommit_batch_sector_quality_adjusted_power_tibs,
        total_provecommit_sector_raw_power_tibs,
        total_provecommit_sector_quality_adjusted_power_tibs,
        total_provecommit_batch_sector_raw_power_tibs,
        daily_new_sector_terminated_raw_power_tibs,
        daily_new_sector_terminated_quality_adjusted_power_tibs,
        total_sector_terminated_raw_power_tibs,
        total_sector_terminated_quality_adjusted_power_tibs,
        daily_new_sector_active_terminated_raw_power_tibs,
        daily_new_sector_active_terminated_quality_adjusted_power_tibs,
        total_sector_active_terminated_raw_power_tibs,
        total_sector_active_terminated_quality_adjusted_power_tibs,
        daily_new_sector_passive_terminated_raw_power_tibs,
        daily_new_sector_passive_terminated_quality_adjusted_power_tibs,
        total_sector_passive_terminated_raw_power_tibs,
        total_sector_passive_terminated_quality_adjusted_power_tibs,
        daily_new_sector_fault_raw_power_tibs,
        daily_new_sector_fault_quality_adjusted_power_tibs,
        active_sector_fault_raw_power_tibs,
        active_sector_fault_quality_adjusted_power_tibs,
        daily_new_sector_recover_raw_power_tibs,
        daily_new_sector_recover_quality_adjusted_power_tibs,
        daily_new_sector_expire_raw_power_tibs,
        daily_new_sector_expire_quality_adjusted_power_tibs,
        total_sector_expire_raw_power_tibs,
        total_sector_expire_quality_adjusted_power_tibs,
        daily_new_sector_extend_raw_power_tibs,
        daily_new_sector_extend_quality_adjusted_power_tibs,
        daily_new_sector_snap_raw_power_tibs,
        daily_new_sector_snap_quality_adjusted_power_tibs,
        total_sector_snap_raw_power_tibs,
        total_sector_snap_quality_adjusted_power_tibs,
        daily_blocks_mined,
        daily_win_count,
        daily_rewards,
        total_blocks_mined,
        total_win_count,
        total_rewards,
        avg_active_sector_duration_days,
        std_active_sector_duration_days,
        spark_retrieval_success_rate,
        total_regular_deal_count,
        total_verified_deal_count,
        daily_new_regular_deal_count,
        daily_new_verified_deal_count,
        active_regular_deal_count,
        active_verified_deal_count,
        total_regular_deal_free_count,
        total_verified_deal_free_count,
        avg_regular_deal_duration_days,
        avg_verified_deal_duration_days,
        total_regular_deal_revenue,
        total_verified_deal_revenue
    from {{ ref("filecoin_daily_storage_providers_metrics") }}
    qualify row_number() over (partition by provider_id order by date desc) = 1
),

provider_metrics_aggregations as (
    select
        provider_id,

        -- Power Aggregations for the last 30 days
        stddev(raw_power_pibs) filter(where date > current_date() - interval '30 days') as stddev_raw_power_pibs_30d,
        stddev(quality_adjusted_power_pibs) filter(where date > current_date() - interval '30 days') as stddev_quality_adjusted_power_pibs_30d,
        stddev(verified_data_power_pibs) filter(where date > current_date() - interval '30 days') as stddev_verified_data_power_pibs_30d,
        avg(smoothed_raw_power_growth_pibs) filter(where date > current_date() - interval '30 days') as avg_smoothed_raw_power_growth_pibs_30d,
        avg(smoothed_quality_adjusted_power_growth_pibs) filter(where date > current_date() - interval '30 days') as avg_smoothed_quality_adjusted_power_growth_pibs_30d,
        avg(smoothed_verified_data_power_growth_pibs) filter(where date > current_date() - interval '30 days') as avg_smoothed_verified_data_power_growth_pibs_30d,

        -- Power Aggregations for the last 3 months
        stddev(raw_power_pibs) filter(where date > current_date() - interval '3 months') as stddev_raw_power_pibs_3m,
        stddev(quality_adjusted_power_pibs) filter(where date > current_date() - interval '3 months') as stddev_quality_adjusted_power_pibs_3m,
        stddev(verified_data_power_pibs) filter(where date > current_date() - interval '3 months') as stddev_verified_data_power_pibs_3m,
        avg(smoothed_raw_power_growth_pibs) filter(where date > current_date() - interval '3 months') as avg_smoothed_raw_power_growth_pibs_3m,
        avg(smoothed_quality_adjusted_power_growth_pibs) filter(where date > current_date() - interval '3 months') as avg_smoothed_quality_adjusted_power_growth_pibs_3m,
        avg(smoothed_verified_data_power_growth_pibs) filter(where date > current_date() - interval '3 months') as avg_smoothed_verified_data_power_growth_pibs_3m,

        -- Power Aggregations for the previous 3 months (mont 6 to 3)
        stddev(raw_power_pibs) filter(where date > current_date() - interval '6 months' and date <= current_date() - interval '3 months') as stddev_raw_power_pibs_3m_6m,
        stddev(quality_adjusted_power_pibs) filter(where date > current_date() - interval '6 months' and date <= current_date() - interval '3 months') as stddev_quality_adjusted_power_pibs_3m_6m,
        stddev(verified_data_power_pibs) filter(where date > current_date() - interval '6 months' and date <= current_date() - interval '3 months') as stddev_verified_data_power_pibs_3m_6m,
        avg(smoothed_raw_power_growth_pibs) filter(where date > current_date() - interval '6 months' and date <= current_date() - interval '3 months') as avg_smoothed_raw_power_growth_pibs_3m_6m,
        avg(smoothed_quality_adjusted_power_growth_pibs) filter(where date > current_date() - interval '6 months' and date <= current_date() - interval '3 months') as avg_smoothed_quality_adjusted_power_growth_pibs_3m_6m,
        avg(smoothed_verified_data_power_growth_pibs) filter(where date > current_date() - interval '6 months' and date <= current_date() - interval '3 months') as avg_smoothed_verified_data_power_growth_pibs_3m_6m,

        -- Power Aggregations for the previous 3 months (mont 9 to 6)
        stddev(raw_power_pibs) filter(where date > current_date() - interval '9 months' and date <= current_date() - interval '6 months') as stddev_raw_power_pibs_6m_9m,
        stddev(quality_adjusted_power_pibs) filter(where date > current_date() - interval '9 months' and date <= current_date() - interval '6 months') as stddev_quality_adjusted_power_pibs_6m_9m,
        stddev(verified_data_power_pibs) filter(where date > current_date() - interval '9 months' and date <= current_date() - interval '6 months') as stddev_verified_data_power_pibs_6m_9m,
        avg(smoothed_raw_power_growth_pibs) filter(where date > current_date() - interval '9 months' and date <= current_date() - interval '6 months') as avg_smoothed_raw_power_growth_pibs_6m_9m,
        avg(smoothed_quality_adjusted_power_growth_pibs) filter(where date > current_date() - interval '9 months' and date <= current_date() - interval '6 months') as avg_smoothed_quality_adjusted_power_growth_pibs_6m_9m,
        avg(smoothed_verified_data_power_growth_pibs) filter(where date > current_date() - interval '9 months' and date <= current_date() - interval '6 months') as avg_smoothed_verified_data_power_growth_pibs_6m_9m,

        -- Power Aggregations for the previous 3 months (mont 12 to 9)
        stddev(raw_power_pibs) filter(where date > current_date() - interval '12 months' and date <= current_date() - interval '9 months') as stddev_raw_power_pibs_9m_12m,
        stddev(quality_adjusted_power_pibs) filter(where date > current_date() - interval '12 months' and date <= current_date() - interval '9 months') as stddev_quality_adjusted_power_pibs_9m_12m,
        stddev(verified_data_power_pibs) filter(where date > current_date() - interval '12 months' and date <= current_date() - interval '9 months') as stddev_verified_data_power_pibs_9m_12m,
        avg(smoothed_raw_power_growth_pibs) filter(where date > current_date() - interval '12 months' and date <= current_date() - interval '9 months') as avg_smoothed_raw_power_growth_pibs_9m_12m,
        avg(smoothed_quality_adjusted_power_growth_pibs) filter(where date > current_date() - interval '12 months' and date <= current_date() - interval '9 months') as avg_smoothed_quality_adjusted_power_growth_pibs_9m_12m,
        avg(smoothed_verified_data_power_growth_pibs) filter(where date > current_date() - interval '12 months' and date <= current_date() - interval '9 months') as avg_smoothed_verified_data_power_growth_pibs_9m_12m,

        -- When they started and stopped providing power
        min(date) filter (where raw_power_pibs > 0) as started_providing_power_at,
        max(date) filter (where raw_power_pibs > 0) as stopped_providing_power_at,

        -- Average uploaded data per day
        avg(onboarded_data_tibs) as avg_data_uploaded_tibs_per_day,
    from {{ ref("filecoin_daily_storage_providers_metrics") }}
    group by provider_id
),

retrieval_data as (
    select
        trim(provider_id) as provider_id,
        mean(spark_retrieval_success_rate) over (partition by provider_id order by date desc rows between 6 preceding and current row) as mean_spark_retrieval_success_rate_7d,
        stddev(spark_retrieval_success_rate) over (partition by provider_id order by date desc rows between 6 preceding and current row) as stddev_spark_retrieval_success_rate_7d
    from {{ ref("filecoin_spark_retrievals") }}
    qualify row_number() over (partition by provider_id order by date desc) = 1
),

energy_name_mapping as (
    select
        trim(provider_id) as provider_id,
        storage_provider_name,
        green_score
    from {{ source("raw_assets", "raw_storage_providers_energy_name_mapping") }}
    qualify row_number() over (partition by trim(provider_id) order by green_score desc) = 1
),

addresses_mapping as (
    select
        id,
        address
    from {{ source("raw_assets", "raw_id_addresses") }}
    qualify row_number() over (partition by id order by height desc) = 1
),

basic_info as (
    select
        trim(provider_id) as provider_id,
        owner_id,
        worker_id,
        peer_id,
        control_addresses,
        multi_addresses,
        sector_size_tibs
    from {{ source("raw_assets", "raw_filecoin_storage_providers_information") }}
)

select
    base.provider_id,
    coalesce(stats.total_deals, 0) as total_deals,
    coalesce(stats.total_verified_deals, 0) as total_verified_deals,
    coalesce(stats.total_active_deals, 0) as total_active_deals,
    coalesce(stats.total_slashed_deals, 0) as total_slashed_deals,
    coalesce(stats.total_finished_deals, 0) as total_finished_deals,
    coalesce(stats.total_active_verified_deals, 0) as total_active_verified_deals,
    coalesce(stats.total_unique_piece_cids, 0) as total_unique_piece_cids,
    coalesce(stats.total_verified_unique_piece_cids, 0) as total_verified_unique_piece_cids,
    coalesce(stats.total_active_unique_piece_cids, 0) as total_active_unique_piece_cids,
    coalesce(stats.total_active_verified_unique_piece_cids, 0) as total_active_verified_unique_piece_cids,
    coalesce(stats.total_data_uploaded_tibs, 0) as total_data_uploaded_tibs,
    coalesce(stats.total_active_data_uploaded_tibs, 0) as total_active_data_uploaded_tibs,
    coalesce(stats.unique_data_uploaded_tibs, 0) as unique_data_uploaded_tibs,
    coalesce(stats.unique_active_data_uploaded_tibs, 0) as unique_active_data_uploaded_tibs,
    coalesce(stats.unique_data_uploaded_ratio, 0) as unique_data_uploaded_ratio,
    coalesce(stats.total_unique_clients, 0) as total_unique_clients,
    coalesce(stats.total_active_unique_clients, 0) as total_active_unique_clients,
    coalesce(stats.total_active_verified_unique_clients, 0) as total_active_verified_unique_clients,
    stats.first_deal_at,
    stats.first_active_deal_at,
    stats.last_deal_at,
    stats.last_active_deal_at,
    stats.last_deal_end_at,
    stats.last_deal_slash_at,
    coalesce(stats.data_uploaded_tibs_30d, 0) as data_uploaded_tibs_30d,
    coalesce(stats.data_uploaded_tibs_6m, 0) as data_uploaded_tibs_6m,
    coalesce(stats.data_uploaded_tibs_1y, 0) as data_uploaded_tibs_1y,
    latest_sp_data.raw_power_pibs,
    latest_sp_data.quality_adjusted_power_pibs,
    latest_sp_data.verified_data_power_pibs,
    latest_sp_data.balance,
    latest_sp_data.initial_pledge,
    latest_sp_data.locked_funds,
    latest_sp_data.pre_commit_deposits,
    latest_sp_data.provider_collateral,
    latest_sp_data.fee_debt,
    latest_sp_data.daily_sector_onboarding_count,
    latest_sp_data.daily_sector_onboarding_raw_power_tibs,
    latest_sp_data.daily_sector_onboarding_quality_adjusted_power_tibs,
    latest_sp_data.total_sector_onboarded_count,
    latest_sp_data.total_sector_onboarding_raw_power_tibs,
    latest_sp_data.total_sector_onboarding_quality_adjusted_power_tibs,
    latest_sp_data.total_sealed_sector_count,
    latest_sp_data.total_precommit_sector_count,
    latest_sp_data.total_precommit_batch_sector_count,
    latest_sp_data.avg_precommit_batch_sector_count,
    latest_sp_data.total_provecommit_sector_count,
    latest_sp_data.total_provecommit_batch_sector_count,
    latest_sp_data.avg_provecommit_batch_sector_count,
    latest_sp_data.total_precommit_sector_raw_power_tibs,
    latest_sp_data.total_precommit_sector_quality_adjusted_power_tibs,
    latest_sp_data.total_precommit_batch_sector_raw_power_tibs,
    latest_sp_data.total_precommit_batch_sector_quality_adjusted_power_tibs,
    latest_sp_data.total_provecommit_sector_raw_power_tibs,
    latest_sp_data.total_provecommit_sector_quality_adjusted_power_tibs,
    latest_sp_data.total_provecommit_batch_sector_raw_power_tibs,
    latest_sp_data.daily_new_sector_terminated_raw_power_tibs,
    latest_sp_data.daily_new_sector_terminated_quality_adjusted_power_tibs,
    latest_sp_data.total_sector_terminated_raw_power_tibs,
    latest_sp_data.total_sector_terminated_quality_adjusted_power_tibs,
    latest_sp_data.daily_new_sector_active_terminated_raw_power_tibs,
    latest_sp_data.daily_new_sector_active_terminated_quality_adjusted_power_tibs,
    latest_sp_data.total_sector_active_terminated_raw_power_tibs,
    latest_sp_data.total_sector_active_terminated_quality_adjusted_power_tibs,
    latest_sp_data.daily_new_sector_passive_terminated_raw_power_tibs,
    latest_sp_data.daily_new_sector_passive_terminated_quality_adjusted_power_tibs,
    latest_sp_data.total_sector_passive_terminated_raw_power_tibs,
    latest_sp_data.total_sector_passive_terminated_quality_adjusted_power_tibs,
    latest_sp_data.daily_new_sector_fault_raw_power_tibs,
    latest_sp_data.daily_new_sector_fault_quality_adjusted_power_tibs,
    latest_sp_data.active_sector_fault_raw_power_tibs,
    latest_sp_data.active_sector_fault_quality_adjusted_power_tibs,
    latest_sp_data.daily_new_sector_recover_raw_power_tibs,
    latest_sp_data.daily_new_sector_recover_quality_adjusted_power_tibs,
    latest_sp_data.daily_new_sector_expire_raw_power_tibs,
    latest_sp_data.daily_new_sector_expire_quality_adjusted_power_tibs,
    latest_sp_data.total_sector_expire_raw_power_tibs,
    latest_sp_data.total_sector_expire_quality_adjusted_power_tibs,
    latest_sp_data.daily_new_sector_extend_raw_power_tibs,
    latest_sp_data.daily_new_sector_extend_quality_adjusted_power_tibs,
    latest_sp_data.daily_new_sector_snap_raw_power_tibs,
    latest_sp_data.daily_new_sector_snap_quality_adjusted_power_tibs,
    latest_sp_data.total_sector_snap_raw_power_tibs,
    latest_sp_data.total_sector_snap_quality_adjusted_power_tibs,
    latest_sp_data.daily_blocks_mined,
    latest_sp_data.daily_win_count,
    latest_sp_data.daily_rewards,
    latest_sp_data.total_blocks_mined,
    latest_sp_data.total_win_count,
    latest_sp_data.total_rewards,
    latest_sp_data.avg_active_sector_duration_days,
    latest_sp_data.std_active_sector_duration_days,
    latest_sp_data.spark_retrieval_success_rate,
    latest_sp_data.total_regular_deal_count,
    latest_sp_data.total_verified_deal_count,
    latest_sp_data.daily_new_regular_deal_count,
    latest_sp_data.daily_new_verified_deal_count,
    latest_sp_data.active_regular_deal_count,
    latest_sp_data.active_verified_deal_count,
    latest_sp_data.total_regular_deal_free_count,
    latest_sp_data.total_verified_deal_free_count,
    latest_sp_data.avg_regular_deal_duration_days,
    storage_provider_location.region,
    storage_provider_location.country,
    storage_provider_location.latitude,
    storage_provider_location.longitude,
    coalesce(energy_name_mapping.storage_provider_name, reputation_data.provider_name) as provider_name,
    reputation_data.is_reachable,
    reputation_data.filrep_uptime_average,
    reputation_data.filrep_score,
    reputation_data.filrep_rank,
    retrieval_data.mean_spark_retrieval_success_rate_7d,
    retrieval_data.stddev_spark_retrieval_success_rate_7d,
    energy_name_mapping.green_score,
    provider_metrics_aggregations.stddev_raw_power_pibs_30d,
    provider_metrics_aggregations.stddev_quality_adjusted_power_pibs_30d,
    provider_metrics_aggregations.stddev_verified_data_power_pibs_30d,
    provider_metrics_aggregations.avg_smoothed_raw_power_growth_pibs_30d,
    provider_metrics_aggregations.avg_smoothed_quality_adjusted_power_growth_pibs_30d,
    provider_metrics_aggregations.avg_smoothed_verified_data_power_growth_pibs_30d,
    provider_metrics_aggregations.stddev_raw_power_pibs_3m,
    provider_metrics_aggregations.stddev_quality_adjusted_power_pibs_3m,
    provider_metrics_aggregations.stddev_verified_data_power_pibs_3m,
    provider_metrics_aggregations.avg_smoothed_raw_power_growth_pibs_3m,
    provider_metrics_aggregations.avg_smoothed_quality_adjusted_power_growth_pibs_3m,
    provider_metrics_aggregations.avg_smoothed_verified_data_power_growth_pibs_3m,
    provider_metrics_aggregations.stddev_raw_power_pibs_3m_6m,
    provider_metrics_aggregations.stddev_quality_adjusted_power_pibs_3m_6m,
    provider_metrics_aggregations.stddev_verified_data_power_pibs_3m_6m,
    provider_metrics_aggregations.avg_smoothed_raw_power_growth_pibs_3m_6m,
    provider_metrics_aggregations.avg_smoothed_quality_adjusted_power_growth_pibs_3m_6m,
    provider_metrics_aggregations.avg_smoothed_verified_data_power_growth_pibs_3m_6m,
    provider_metrics_aggregations.stddev_raw_power_pibs_6m_9m,
    provider_metrics_aggregations.stddev_quality_adjusted_power_pibs_6m_9m,
    provider_metrics_aggregations.stddev_verified_data_power_pibs_6m_9m,
    provider_metrics_aggregations.avg_smoothed_raw_power_growth_pibs_6m_9m,
    provider_metrics_aggregations.avg_smoothed_quality_adjusted_power_growth_pibs_6m_9m,
    provider_metrics_aggregations.avg_smoothed_verified_data_power_growth_pibs_6m_9m,
    provider_metrics_aggregations.stddev_raw_power_pibs_9m_12m,
    provider_metrics_aggregations.stddev_quality_adjusted_power_pibs_9m_12m,
    provider_metrics_aggregations.stddev_verified_data_power_pibs_9m_12m,
    provider_metrics_aggregations.avg_smoothed_raw_power_growth_pibs_9m_12m,
    provider_metrics_aggregations.avg_smoothed_quality_adjusted_power_growth_pibs_9m_12m,
    provider_metrics_aggregations.avg_smoothed_verified_data_power_growth_pibs_9m_12m,
    provider_metrics_aggregations.started_providing_power_at,
    provider_metrics_aggregations.stopped_providing_power_at,
    addresses_mapping.address,
    basic_info.owner_id,
    basic_info.worker_id,
    basic_info.peer_id,
    basic_info.control_addresses,
    basic_info.multi_addresses,
    basic_info.sector_size_tibs,
    avg_data_uploaded_tibs_per_day,
    ((total_active_data_uploaded_tibs / 1024) / latest_sp_data.raw_power_pibs) as capacity_utilization_ratio
from base_providers as base
left join stats on base.provider_id = stats.provider_id
left join storage_provider_location on base.provider_id = storage_provider_location.provider_id
left join reputation_data on base.provider_id = reputation_data.provider_id
left join latest_sp_data on base.provider_id = latest_sp_data.provider_id
left join retrieval_data on base.provider_id = retrieval_data.provider_id
left join energy_name_mapping on base.provider_id = energy_name_mapping.provider_id
left join provider_metrics_aggregations on base.provider_id = provider_metrics_aggregations.provider_id
left join addresses_mapping on base.provider_id = addresses_mapping.id
left join basic_info on base.provider_id = basic_info.provider_id
