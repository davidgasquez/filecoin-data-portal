-- asset.description = Miner power and lifetime activity.

-- asset.depends = model.network_daily_miner_power
-- asset.depends = model.network_daily_miner_sector_lifecycle
-- asset.depends = model.network_daily_miner_block_rewards
-- asset.depends = model.network_miner_market_deal_activity

-- asset.column = miner_id | Filecoin storage provider actor id address.
-- asset.column = raw_power_tibs | Current raw byte power, in tebibytes.
-- asset.column = quality_adjusted_power_tibs | Current quality adjusted power, in tebibytes.
-- asset.column = has_power | Whether the provider currently has positive power.
-- asset.column = has_sector_activity | Whether the provider has sector lifecycle activity.
-- asset.column = has_market_deals | Whether the provider has market deal activity.
-- asset.column = first_sector_activity_date | First date with sector lifecycle activity.
-- asset.column = last_sector_activity_date | Most recent date with sector lifecycle activity.
-- asset.column = first_market_deal_start_at | First observed market deal start timestamp.
-- asset.column = last_market_deal_start_at | Most recent market deal start timestamp.
-- asset.column = total_block_rewards_fil | Total minted block rewards allocated to the provider on observable tipsets, in FIL. Partial when unobservable_win_count > 0, null when all wins are unobservable.
-- asset.column = unobservable_win_count | Lifetime winning proofs on tipsets whose rewards are unobservable and excluded from total_block_rewards_fil.

-- asset.not_null = miner_id
-- asset.not_null = has_power
-- asset.not_null = has_sector_activity
-- asset.not_null = has_market_deals
-- asset.unique = miner_id

with current_power as (
    select
        miner_id,
        raw_power_tibs,
        quality_adjusted_power_tibs,
        has_power
    from model.network_daily_miner_power
    where date = (select max(date) from model.network_daily_miner_power)
),
sector_activity as (
    select
        miner_id,
        min(date) as first_sector_activity_date,
        max(date) as last_sector_activity_date,
        true as has_sector_activity
    from model.network_daily_miner_sector_lifecycle
    group by 1
),
reward_activity as (
    select
        miner_id,
        sum(block_rewards_fil) as total_block_rewards_fil,
        sum(unobservable_win_count) as unobservable_win_count
    from model.network_daily_miner_block_rewards
    group by 1
),
market_deal_activity as (
    select
        miner_id,
        first_market_deal_start_at,
        last_market_deal_start_at,
        true as has_market_deals
    from model.network_miner_market_deal_activity
),
miner_ids as (
    select distinct miner_id from model.network_daily_miner_sector_lifecycle
    union
    select miner_id from current_power
    union
    select miner_id from reward_activity
    union
    select miner_id from market_deal_activity
)
select
    miner_ids.miner_id,
    current_power.raw_power_tibs,
    current_power.quality_adjusted_power_tibs,
    coalesce(current_power.has_power, false) as has_power,
    coalesce(sector_activity.has_sector_activity, false) as has_sector_activity,
    coalesce(market_deal_activity.has_market_deals, false) as has_market_deals,
    sector_activity.first_sector_activity_date,
    sector_activity.last_sector_activity_date,
    market_deal_activity.first_market_deal_start_at,
    market_deal_activity.last_market_deal_start_at,
    if(reward_activity.miner_id is null, 0, reward_activity.total_block_rewards_fil)
        as total_block_rewards_fil,
    coalesce(reward_activity.unobservable_win_count, 0) as unobservable_win_count
from miner_ids
left join current_power
    using (miner_id)
left join sector_activity
    using (miner_id)
left join market_deal_activity
    using (miner_id)
left join reward_activity
    using (miner_id)
order by quality_adjusted_power_tibs desc nulls last, miner_id
