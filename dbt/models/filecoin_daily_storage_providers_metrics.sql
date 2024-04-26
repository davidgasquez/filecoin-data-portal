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

rewards_data as (
    select
        stat_date::date as date,
        miner_id as provider_id,
        blocks_mined,
        win_count,
        rewards
    from {{ source("raw_assets", "raw_storage_providers_rewards") }}
    where date is not null and provider_id is not null
)

select
    dc.date,
    coalesce(dm.provider_id, spp.provider_id, tbd.provider_id, rd.provider_id) as provider_id,
    dm.onboarded_data_tibs,
    dm.deals,
    dm.unique_piece_cids,
    dm.unique_deal_making_clients,
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
    rd.blocks_mined,
    rd.win_count,
    rd.rewards
from date_calendar dc
full outer join deal_metrics dm on dc.date = dm.date
full outer join storage_providers_power spp on dc.date = spp.date and dm.provider_id = spp.provider_id
full outer join token_balance_data tbd on dc.date = tbd.date and dm.provider_id = tbd.provider_id
full outer join rewards_data rd on dc.date = rd.date and dm.provider_id = rd.provider_id
where dc.date >= '2020-09-12'
order by dc.date desc
