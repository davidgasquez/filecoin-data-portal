-- asset.description = Daily storage provider block rewards allocated from network rewards.
-- asset.resource = bigquery.lily

-- asset.column = date | UTC date.
-- asset.column = provider_id | Filecoin storage provider actor id address.
-- asset.column = blocks_mined | Block headers mined by the provider on the date.
-- asset.column = win_count | Winning proofs recorded by the provider on the date.
-- asset.column = block_rewards_fil | Exact block rewards allocated to the provider on the date, in FIL.

-- asset.not_null = date
-- asset.not_null = provider_id
-- asset.not_null = blocks_mined
-- asset.not_null = win_count
-- asset.not_null = block_rewards_fil
-- asset.assert = blocks_mined > 0
-- asset.assert = win_count > 0

with chain_rewards as (
    select
        height,
        min(cast(total_mined_reward as bignumeric)) as total_mined_reward_atto
    from `chain_rewards`
    group by 1
), reward_deltas as (
    select
        height,
        total_mined_reward_atto
            - lag(total_mined_reward_atto) over (order by height)
            as block_rewards_atto
    from chain_rewards
), network_blocks as (
    select
        height,
        sum(win_count) as network_win_count
    from `block_headers`
    where height > 0
    group by 1
), provider_blocks as (
    select
        date(timestamp_seconds((height * 30) + 1598306400)) as date,
        height,
        miner as provider_id,
        count(*) as blocks_mined,
        sum(win_count) as win_count
    from `block_headers`
    where height > 0
    group by 1, 2, 3
)
select
    provider_blocks.date,
    provider_blocks.provider_id,
    sum(provider_blocks.blocks_mined) as blocks_mined,
    sum(provider_blocks.win_count) as win_count,
    cast(
        sum(
            reward_deltas.block_rewards_atto
            * cast(provider_blocks.win_count as bignumeric)
            / cast(network_blocks.network_win_count as bignumeric)
        ) / cast('1000000000000000000' as bignumeric)
        as float64
    ) as block_rewards_fil
from provider_blocks
join reward_deltas
    using (height)
join network_blocks
    using (height)
where reward_deltas.block_rewards_atto is not null
  and network_blocks.network_win_count > 0
group by 1, 2
order by date desc, provider_id
