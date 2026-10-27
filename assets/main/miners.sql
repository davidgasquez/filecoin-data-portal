-- asset.description = Filecoin miners metrics and latest details.

-- asset.depends = model.network_miners

-- asset.column = miner_id | Filecoin storage provider actor id address.
-- asset.column = owner_id | Current owner actor id address.
-- asset.column = worker_id | Current worker actor id address.
-- asset.column = beneficiary_id | Current beneficiary actor id address.
-- asset.column = peer_id | Current libp2p peer id.
-- asset.column = control_addresses | Current JSON array of control addresses.
-- asset.column = multi_addresses | Current JSON array of multiaddrs.
-- asset.column = sector_size | Current sector size in bytes.
-- asset.column = live_sectors | Current live sector count.
-- asset.column = active_sectors | Current active sector count.
-- asset.column = faulty_sectors | Current faulty sector count.
-- asset.column = actor_balance_fil | Current storage provider actor balance, in FIL.
-- asset.column = available_balance_fil | Current available storage provider balance, in FIL.
-- asset.column = market_escrow_fil | Current market escrow balance, in FIL.
-- asset.column = market_locked_fil | Current market locked balance, in FIL.
-- asset.column = market_available_fil | Current market available balance, in FIL.
-- asset.column = initial_pledge_fil | Current initial pledge, in FIL.
-- asset.column = locked_funds_fil | Current locked funds, in FIL.
-- asset.column = pre_commit_deposits_fil | Current pre-commit deposits, in FIL.
-- asset.column = fee_debt_fil | Current fee debt, in FIL.
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
