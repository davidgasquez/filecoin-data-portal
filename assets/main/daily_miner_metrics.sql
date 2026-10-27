-- asset.description = Daily metrics for storage providers.

-- asset.depends = model.network_daily_miner_power
-- asset.depends = model.network_daily_miner_sector_lifecycle
-- asset.depends = model.network_daily_miner_block_rewards
-- asset.depends = raw.coincodex_market_data

-- asset.column = date | UTC date.
-- asset.column = miner_id | Filecoin storage provider actor id address.
-- asset.column = raw_power_tibs | End-of-day raw byte power, in tebibytes.
-- asset.column = quality_adjusted_power_tibs | End-of-day quality adjusted power, in tebibytes.
-- asset.column = onboarded_tibs | Raw data onboarded on the date, in tebibytes.
-- asset.column = onboarded_sectors | Sectors onboarded on the date.
-- asset.column = terminated_tibs | Raw data terminated on the date, in tebibytes.
-- asset.column = terminated_sectors | Sectors terminated on the date.
-- asset.column = expired_tibs | Raw data expired on the date, in tebibytes.
-- asset.column = expired_sectors | Sectors expired on the date.
-- asset.column = removed_tibs | Raw data removed on the date, in tebibytes.
-- asset.column = removed_sectors | Sectors removed on the date.
-- asset.column = blocks_mined | Block headers mined by the provider on the date.
-- asset.column = win_count | Winning proofs recorded by the provider on the date.
-- asset.column = block_rewards_fil | Minted block rewards allocated to the provider on observable tipsets, in FIL. Partial when unobservable_win_count > 0, null when all wins are unobservable. Excludes message rewards and, since Solstice, service and burn allocations.
-- asset.column = block_rewards_usd | block_rewards_fil valued with the daily average FIL price, in USD.
-- asset.column = unobservable_win_count | Winning proofs on tipsets whose rewards are unobservable and excluded from block_rewards_fil.

-- asset.not_null = date
-- asset.not_null = miner_id
-- asset.not_null = raw_power_tibs
-- asset.not_null = quality_adjusted_power_tibs
-- asset.not_null = onboarded_tibs
-- asset.not_null = onboarded_sectors
-- asset.not_null = terminated_tibs
-- asset.not_null = terminated_sectors
-- asset.not_null = expired_tibs
-- asset.not_null = expired_sectors
-- asset.not_null = removed_tibs
-- asset.not_null = removed_sectors
-- asset.not_null = blocks_mined
-- asset.not_null = win_count
-- asset.not_null = unobservable_win_count

with market_data as (
    select
        cast(time_start as date) as date,
        price_avg_usd as fil_token_price_avg_usd
    from raw.coincodex_market_data
), miner_dates as (
    select date, miner_id from model.network_daily_miner_power
    union
    select date, miner_id from model.network_daily_miner_sector_lifecycle
    union
    select date, miner_id from model.network_daily_miner_block_rewards
)
select
    miner_dates.date,
    miner_dates.miner_id,
    coalesce(power.raw_power_tibs, 0) as raw_power_tibs,
    coalesce(power.quality_adjusted_power_tibs, 0) as quality_adjusted_power_tibs,
    coalesce(sector_lifecycle.onboarded_tibs, 0) as onboarded_tibs,
    coalesce(sector_lifecycle.onboarded_sectors, 0) as onboarded_sectors,
    coalesce(sector_lifecycle.terminated_tibs, 0) as terminated_tibs,
    coalesce(sector_lifecycle.terminated_sectors, 0) as terminated_sectors,
    coalesce(sector_lifecycle.expired_tibs, 0) as expired_tibs,
    coalesce(sector_lifecycle.expired_sectors, 0) as expired_sectors,
    coalesce(sector_lifecycle.removed_tibs, 0) as removed_tibs,
    coalesce(sector_lifecycle.removed_sectors, 0) as removed_sectors,
    coalesce(block_rewards.blocks_mined, 0) as blocks_mined,
    coalesce(block_rewards.win_count, 0) as win_count,
    if(block_rewards.miner_id is null, 0, block_rewards.block_rewards_fil)
        as block_rewards_fil,
    if(block_rewards.miner_id is null, 0, block_rewards.block_rewards_fil)
        * market_data.fil_token_price_avg_usd as block_rewards_usd,
    coalesce(block_rewards.unobservable_win_count, 0) as unobservable_win_count
from miner_dates
left join model.network_daily_miner_power as power
    using (date, miner_id)
left join model.network_daily_miner_sector_lifecycle as sector_lifecycle
    using (date, miner_id)
left join model.network_daily_miner_block_rewards as block_rewards
    using (date, miner_id)
left join market_data
    using (date)
order by date desc, miner_id
