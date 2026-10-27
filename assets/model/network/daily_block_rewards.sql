-- asset.description = Daily Filecoin block rewards minted and allocated across observable tipsets.
-- asset.depends = model.network_block_rewards_by_height

-- asset.column = date | UTC date.
-- asset.column = blocks_mined | Known blocks mined on the date.
-- asset.column = win_count | Known winning proofs on the date.
-- asset.column = minted_rewards_fil | Block rewards minted on observable tipsets, in FIL.
-- asset.column = miner_rewards_fil | Minted rewards allocated to block miners on observable tipsets, in FIL. Excludes message rewards.
-- asset.column = service_rewards_fil | Minted rewards allocated to the service stream on observable tipsets, in FIL.
-- asset.column = burn_rewards_fil | Minted rewards allocated to burn by the reward distribution on observable tipsets, in FIL.
-- asset.column = reward_per_wincount_fil | Miner rewards per observable win count, in FIL.
-- asset.column = tipsets | Tipsets recorded on the date by block headers, reward distributions, or reward actor state.
-- asset.column = unobservable_tipsets | Recorded tipsets whose rewards are unobservable and excluded from reward sums, including tipsets without block headers.
-- asset.column = unobservable_win_count | Known winning proofs on unobservable tipsets.

-- asset.not_null = date
-- asset.not_null = blocks_mined
-- asset.not_null = win_count
-- asset.not_null = tipsets
-- asset.not_null = unobservable_tipsets
-- asset.not_null = unobservable_win_count
-- asset.unique = date
-- asset.assert = unobservable_tipsets between 0 and tipsets
-- asset.assert = unobservable_tipsets = tipsets or minted_rewards_fil is not null

select
    date,
    coalesce(sum(blocks_mined), 0) as blocks_mined,
    coalesce(sum(network_win_count), 0) as win_count,
    sum(minted_rewards_fil) as minted_rewards_fil,
    sum(miner_rewards_fil) as miner_rewards_fil,
    sum(service_rewards_fil) as service_rewards_fil,
    sum(burn_rewards_fil) as burn_rewards_fil,
    sum(miner_rewards_fil)
        / nullif(sum(network_win_count) filter (where reward_source != 'unobservable'), 0)
        as reward_per_wincount_fil,
    count(*) as tipsets,
    count(*) filter (where reward_source = 'unobservable') as unobservable_tipsets,
    coalesce(
        sum(network_win_count) filter (where reward_source = 'unobservable'), 0
    ) as unobservable_win_count
from model.network_block_rewards_by_height
group by 1
order by date desc
