-- asset.description = Daily storage provider block rewards from tipset reward allocations.
-- asset.resource = bigquery.lily

-- asset.column = date | UTC date.
-- asset.column = miner_id | Filecoin storage provider actor id address.
-- asset.column = blocks_mined | Blocks mined by the provider on the date.
-- asset.column = win_count | Winning proofs recorded by the provider on the date.
-- asset.column = block_rewards_fil | Minted rewards allocated to the provider on observable tipsets, in FIL. Partial when unobservable_win_count > 0, null when all its wins are unobservable. Excludes message rewards and, since Solstice, service and burn allocations.
-- asset.column = unobservable_win_count | Winning proofs on tipsets whose rewards are unobservable and excluded from block_rewards_fil.

-- asset.not_null = date
-- asset.not_null = miner_id
-- asset.not_null = blocks_mined
-- asset.not_null = win_count
-- asset.not_null = unobservable_win_count
-- asset.assert = blocks_mined > 0
-- asset.assert = win_count > 0
-- asset.assert = unobservable_win_count between 0 and win_count
-- asset.assert = (block_rewards_fil is null) = (unobservable_win_count = win_count)

with headers as (
    select
        height,
        count(distinct parent_state_root) as parent_states,
        any_value(parent_state_root) as parent_state_root,
        sum(win_count) as network_win_count
    from `block_headers`
    where height > 0
    group by 1
), rewards as (
    -- Reward actor state at the tipset's parent state root; see network_block_rewards_by_height.
    select
        rewards.height,
        count(*) = 1
            and coalesce(
                any_value(headers.parent_states) = 1
                and any_value(headers.parent_state_root) = any_value(rewards.state_root),
                true
            ) as is_canonical,
        any_value(cast(rewards.total_mined_reward as bignumeric))
            as total_mined_reward_atto,
        any_value(cast(rewards.new_reward as bignumeric)) as epoch_reward_atto,
        any_value(headers.network_win_count) as network_win_count
    from `chain_rewards` as rewards
    left join headers
        using (height)
    where rewards.height < 6470400
    group by 1
), heights as (
    select height, lead(height) over (order by height) as next_height
    from (
        select height from headers
        union distinct
        select height from rewards where height > 0
    )
), reward_deltas as (
    select
        height,
        if(
            is_canonical
                and lead(is_canonical) over (order by height)
                and lead(height) over (order by height) = heights.next_height
                and abs(
                    lead(total_mined_reward_atto) over (order by height)
                        - total_mined_reward_atto
                        - epoch_reward_atto * network_win_count / 5
                ) < epoch_reward_atto / 10,
            lead(total_mined_reward_atto) over (order by height) - total_mined_reward_atto,
            null
        ) as minted_atto
    from rewards
    join heights
        using (height)
), pre_solstice_blocks as (
    select
        blocks.height,
        blocks.miner as miner_id,
        blocks.win_count,
        reward_deltas.minted_atto
            * blocks.win_count
            / headers.network_win_count as miner_atto
    from `block_headers` as blocks
    join headers
        using (height)
    left join reward_deltas
        using (height)
    where blocks.height > 0
      and blocks.height < 6470280
), distributions as (
    select height, any_value(distribution) as distribution
    from `chain_reward_distributions`
    group by 1
    having count(*) = 1
), distribution_blocks as (
    select
        distributions.height,
        json_value(block, '$.Miner') as miner_id,
        cast(json_value(block, '$.WinCount') as int64) as win_count,
        cast(json_value(block, '$.Amounts.MinerReward') as bignumeric) as miner_atto
    from distributions,
        unnest(json_query_array(distributions.distribution, '$.Blocks')) as block
), post_solstice_blocks as (
    select height, miner_id, win_count, miner_atto
    from distribution_blocks

    union all

    -- Headers without a reward distribution have unobservable allocations.
    select blocks.height, blocks.miner, blocks.win_count, null
    from `block_headers` as blocks
    left join distributions
        using (height)
    where blocks.height >= 6470280
      and distributions.height is null
), blocks as (
    select * from pre_solstice_blocks
    union all
    select * from post_solstice_blocks
)
select
    date(timestamp_seconds((height * 30) + 1598306400)) as date,
    miner_id,
    count(*) as blocks_mined,
    sum(win_count) as win_count,
    cast(sum(miner_atto) / 1e18 as float64) as block_rewards_fil,
    sum(if(miner_atto is null, win_count, 0)) as unobservable_win_count
from blocks
where date(timestamp_seconds((height * 30) + 1598306400)) < current_date()
group by 1, 2
order by date desc, miner_id
