-- asset.description = Miner power and lifetime activity.

-- asset.depends = model.network_miners

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

select *
from model.network_miners
order by quality_adjusted_power_tibs desc nulls last, miner_id
