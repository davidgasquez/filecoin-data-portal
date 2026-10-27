-- asset.description = Filecoin block rewards minted and allocated per tipset height.
-- asset.resource = bigquery.lily

-- asset.column = height | Tipset height recorded by block headers, reward distributions, or reward actor state.
-- asset.column = date | UTC date derived from height.
-- asset.column = blocks_mined | Known blocks in the tipset, from block headers or the reward distribution. Null when neither is recorded.
-- asset.column = network_win_count | Known winning proofs in the tipset, from block headers or the reward distribution. Null when neither is recorded.
-- asset.column = minted_rewards_fil | Block rewards minted by the reward actor for the tipset, in FIL. Null when unobservable.
-- asset.column = miner_rewards_fil | Minted rewards allocated to block miners (consensus stream since Solstice), in FIL. Excludes message rewards. Null when unobservable.
-- asset.column = service_rewards_fil | Minted rewards allocated to the service stream, in FIL. Zero before Solstice, null when unobservable.
-- asset.column = burn_rewards_fil | Minted rewards allocated to burn by the reward distribution, in FIL. Zero before Solstice, null when unobservable.
-- asset.column = reward_per_wincount_fil | Miner rewards per win count, in FIL.
-- asset.column = reward_source | `distribution` (Lotus reward distribution, since Solstice), `reward_delta` (change in reward actor minted total, before Solstice), or `unobservable`.

-- asset.not_null = height
-- asset.not_null = date
-- asset.not_null = reward_source
-- asset.unique = height
-- asset.assert = height > 0
-- asset.assert = reward_source in ('distribution', 'reward_delta', 'unobservable')
-- asset.assert = (reward_source = 'unobservable') = (miner_rewards_fil is null)
-- asset.assert = reward_source != 'distribution' or height >= 6470280
-- asset.assert = reward_source != 'reward_delta' or height < 6470280
-- asset.assert = height >= 6470280 or (service_rewards_fil = 0 and burn_rewards_fil = 0)
-- asset.assert = reward_source = 'unobservable' or abs(minted_rewards_fil - miner_rewards_fil - service_rewards_fil - burn_rewards_fil) < 0.000001

with headers as (
    select
        height,
        count(*) as blocks_mined,
        sum(win_count) as network_win_count,
        count(distinct parent_state_root) as parent_states,
        any_value(parent_state_root) as parent_state_root
    from `block_headers`
    where height > 0
    group by 1
), distributions as (
    -- One row per executed tipset; tipset keys match block header CIDs.
    select
        height,
        array_length(json_query_array(distribution, '$.Blocks')) as blocks_mined,
        (
            select sum(cast(json_value(block, '$.WinCount') as int64))
            from unnest(json_query_array(distribution, '$.Blocks')) as block
        ) as network_win_count,
        cast(json_value(distribution, '$.Totals.MintedReward') as bignumeric)
            as minted_atto,
        cast(json_value(distribution, '$.Totals.MinerReward') as bignumeric)
            as miner_atto,
        cast(json_value(distribution, '$.Totals.ExplicitReward') as bignumeric)
            as service_atto,
        cast(json_value(distribution, '$.Totals.BurnAllocation') as bignumeric)
            as burn_atto,
        count(*) over (partition by height) = 1 as is_unique
    from `chain_reward_distributions`
    qualify row_number() over (partition by height) = 1
), rewards as (
    -- Rows hold reward actor state at the tipset's parent state root, so the
    -- tipset's reward is the next row minus this one. Heights with duplicate
    -- rows or forked headers are ambiguous. Deltas off by half a win or more
    -- from new_reward * wins / 5 (AwardBlockReward) include rewards from
    -- tipsets missing in every source, or headers that were never rewarded.
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
        any_value(cast(rewards.new_reward as bignumeric)) as epoch_reward_atto
    from `chain_rewards` as rewards
    left join headers
        using (height)
    group by 1
), reward_deltas as (
    select
        height,
        epoch_reward_atto,
        lead(height) over (order by height) as next_reward_height,
        is_canonical and lead(is_canonical) over (order by height) as is_canonical,
        lead(total_mined_reward_atto) over (order by height)
            - total_mined_reward_atto as minted_atto
    from rewards
), heights as (
    select height, lead(height) over (order by height) as next_height
    from (
        select height from headers
        union distinct
        select height from distributions
        union distinct
        select height from rewards where height > 0
    )
), allocations as (
    select
        heights.height,
        coalesce(headers.blocks_mined, distributions.blocks_mined) as blocks_mined,
        coalesce(headers.network_win_count, distributions.network_win_count)
            as network_win_count,
        if(
            heights.height < 6470280
                and reward_deltas.is_canonical
                and reward_deltas.next_reward_height = heights.next_height
                and abs(
                    reward_deltas.minted_atto
                        - reward_deltas.epoch_reward_atto * headers.network_win_count / 5
                ) < reward_deltas.epoch_reward_atto / 10,
            reward_deltas.minted_atto,
            null
        ) as delta_atto,
        if(distributions.is_unique, distributions.minted_atto, null) as minted_atto,
        if(distributions.is_unique, distributions.miner_atto, null) as miner_atto,
        if(distributions.is_unique, distributions.service_atto, null) as service_atto,
        if(distributions.is_unique, distributions.burn_atto, null) as burn_atto
    from heights
    left join headers
        using (height)
    left join distributions
        using (height)
    left join reward_deltas
        using (height)
), rewards_by_height as (
    select
        height,
        blocks_mined,
        network_win_count,
        if(height < 6470280, delta_atto, minted_atto) as minted_atto,
        if(height < 6470280, delta_atto, miner_atto) as miner_atto,
        if(height < 6470280, 0, service_atto) as service_atto,
        if(height < 6470280, 0, burn_atto) as burn_atto,
        case
            when height < 6470280 and delta_atto is not null then 'reward_delta'
            when height >= 6470280 and miner_atto is not null then 'distribution'
            else 'unobservable'
        end as reward_source
    from allocations
)
select
    height,
    date(timestamp_seconds((height * 30) + 1598306400)) as date,
    blocks_mined,
    network_win_count,
    cast(minted_atto / 1e18 as float64) as minted_rewards_fil,
    cast(miner_atto / 1e18 as float64) as miner_rewards_fil,
    cast(service_atto / 1e18 as float64) as service_rewards_fil,
    cast(burn_atto / 1e18 as float64) as burn_rewards_fil,
    cast(miner_atto / network_win_count / 1e18 as float64) as reward_per_wincount_fil,
    reward_source
from rewards_by_height
where date(timestamp_seconds((height * 30) + 1598306400)) < current_date()
order by height desc
