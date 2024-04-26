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
    from {{ source("raw_assets", "raw_spark_retrieval_success_rate") }}
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
        fee_debt
    from {{ ref("filecoin_daily_storage_providers_metrics") }}
    qualify row_number() over (partition by provider_id order by date desc) = 1
),

rewards_data as (
    select
        trim(miner_id) as provider_id,
        sum(blocks_mined) as total_blocks_mined,
        sum(win_count) as total_win_count,
        sum(rewards) as total_rewards_fil,
    from {{ source("raw_assets", "raw_storage_providers_rewards") }}
    group by provider_id
),

retrieval_data as (
    select
        trim(provider_id) as provider_id,
        mean(success_rate) over(partition by provider_id order by date desc rows between 6 preceding and current row) as mean_spark_retrieval_success_rate_7d,
        stddev(success_rate) over(partition by provider_id order by date desc rows between 6 preceding and current row) as stddev_spark_retrieval_success_rate_7d
    from {{ source("raw_assets", "raw_spark_retrieval_success_rate") }}
    qualify row_number() over (partition by provider_id order by date desc) = 1
),

energy_name_mapping as (
    select
        trim(provider_id) as provider_id,
        storage_provider_name,
        green_score
    from {{ source("raw_assets", "raw_storage_providers_energy_name_mapping") }}
    qualify row_number() over (partition by trim(provider_id) order by green_score desc) = 1
)

select
    base.provider_id,
    stats.total_deals,
    stats.total_verified_deals,
    stats.total_active_deals,
    stats.total_active_verified_deals,
    stats.total_unique_piece_cids,
    stats.total_verified_unique_piece_cids,
    stats.total_active_unique_piece_cids,
    stats.total_active_verified_unique_piece_cids,
    stats.total_data_uploaded_tibs,
    stats.total_active_data_uploaded_tibs,
    stats.unique_data_uploaded_tibs,
    stats.unique_active_data_uploaded_tibs,
    stats.unique_data_uploaded_ratio,
    stats.total_unique_clients,
    stats.total_active_unique_clients,
    stats.total_active_verified_unique_clients,
    stats.first_deal_at,
    stats.first_active_deal_at,
    stats.last_deal_at,
    stats.last_active_deal_at,
    stats.data_uploaded_tibs_30d,
    stats.data_uploaded_tibs_6m,
    stats.data_uploaded_tibs_1y,
    latest_sp_data.raw_power_pibs,
    latest_sp_data.quality_adjusted_power_pibs,
    latest_sp_data.verified_data_power_pibs,
    latest_sp_data.balance,
    latest_sp_data.initial_pledge,
    latest_sp_data.locked_funds,
    latest_sp_data.pre_commit_deposits,
    latest_sp_data.provider_collateral,
    latest_sp_data.fee_debt,
    storage_provider_location.region,
    storage_provider_location.country,
    storage_provider_location.latitude,
    storage_provider_location.longitude,
    coalesce(energy_name_mapping.storage_provider_name, reputation_data.provider_name) as provider_name,
    reputation_data.is_reachable,
    reputation_data.filrep_uptime_average,
    reputation_data.filrep_score,
    reputation_data.filrep_rank,
    rewards_data.total_blocks_mined,
    rewards_data.total_win_count,
    rewards_data.total_rewards_fil,
    retrieval_data.mean_spark_retrieval_success_rate_7d,
    retrieval_data.stddev_spark_retrieval_success_rate_7d,
    energy_name_mapping.green_score
from base_providers as base
left join stats on base.provider_id = stats.provider_id
left join storage_provider_location on base.provider_id = storage_provider_location.provider_id
left join reputation_data on base.provider_id = reputation_data.provider_id
left join latest_sp_data on base.provider_id = latest_sp_data.provider_id
left join rewards_data on base.provider_id = rewards_data.provider_id
left join retrieval_data on base.provider_id = retrieval_data.provider_id
left join energy_name_mapping on base.provider_id = energy_name_mapping.provider_id
