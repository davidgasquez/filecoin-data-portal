-- asset.description = Filecoin block rewards and winning counts by height.
-- asset.resource = bigquery.lily

-- asset.column = height | Chain epoch height.
-- asset.column = date | UTC date derived from height.
-- asset.column = blocks_mined | Block headers mined at the height.
-- asset.column = network_win_count | Winning proofs recorded at the height.
-- asset.column = block_rewards_fil | Exact block rewards minted at the height, in FIL.
-- asset.column = reward_per_wincount_fil | Exact reward allocated per win count at the height, in FIL.

-- asset.not_null = height
-- asset.not_null = date
-- asset.not_null = blocks_mined
-- asset.not_null = network_win_count
-- asset.not_null = block_rewards_fil
-- asset.not_null = reward_per_wincount_fil
-- asset.unique = height
-- asset.assert = height > 0
-- asset.assert = blocks_mined > 0
-- asset.assert = network_win_count > 0

with constants as (
    select cast('1000000000000000000' as bignumeric) as atto_per_fil
), chain_rewards as (
    select
        height,
        min(cast(total_mined_reward as bignumeric)) as total_mined_reward_atto
    from `chain_rewards`
    group by 1
), reward_deltas as (
    select
        height,
        date(timestamp_seconds((height * 30) + 1598306400)) as date,
        total_mined_reward_atto
            - lag(total_mined_reward_atto) over (order by height)
            as block_rewards_atto
    from chain_rewards
), network_blocks as (
    select
        height,
        count(*) as blocks_mined,
        sum(win_count) as network_win_count
    from `block_headers`
    where height > 0
    group by 1
)
select
    rewards.height,
    rewards.date,
    network_blocks.blocks_mined,
    network_blocks.network_win_count,
    cast(
        rewards.block_rewards_atto / constants.atto_per_fil
        as float64
    ) as block_rewards_fil,
    cast(
        rewards.block_rewards_atto
        / cast(network_blocks.network_win_count as bignumeric)
        / constants.atto_per_fil
        as float64
    ) as reward_per_wincount_fil
from reward_deltas as rewards
join network_blocks
    using (height)
cross join constants
where rewards.block_rewards_atto is not null
  and network_blocks.network_win_count > 0
order by rewards.height desc
