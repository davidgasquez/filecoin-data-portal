-- asset.description = Daily onchain activity, gas, and burn totals.

-- asset.depends = raw.lily_daily_network_activity_by_method
-- asset.depends = raw.lily_daily_network_burn
-- asset.depends = raw.lily_daily_miner_cron_fees
-- asset.depends = model.network_daily_block_rewards

-- asset.column = date | UTC date.
-- asset.column = gas_used_millions | Total gas used, in millions.
-- asset.column = transactions | Onchain transactions.
-- asset.column = total_value_fil | FIL transferred by top-level messages.
-- asset.column = total_gas_fee_fil | FIL paid in gas fees.
-- asset.column = base_fee_burn_fil | FIL burned by message base fees.
-- asset.column = overestimation_burn_fil | FIL burned by gas overestimation.
-- asset.column = message_burn_fil | FIL burned by message execution.
-- asset.column = miner_tip_fil | FIL paid to miners as message tips.
-- asset.column = message_storage_provider_penalty_fil | FIL penalties incurred by storage providers during message execution.
-- asset.column = total_value_flow_fil | FIL value transferred plus gas fees.
-- asset.column = storage_provider_cron_burn_fil | FIL burned during storage provider cron events. Null before Lily cron fee coverage.
-- asset.column = storage_provider_cron_fee_assessed_fil | FIL fees assessed during storage provider cron events, not necessarily burned.
-- asset.column = storage_provider_cron_penalty_assessed_fil | FIL penalties assessed during storage provider cron events, not necessarily burned.
-- asset.column = total_burn_fil | Total FIL burned on-chain, including emission burn.
-- asset.column = emission_burn_fil | Newly minted block reward FIL burned as the FIP-0118 residual. Null when reward allocation is unknown.
-- asset.column = non_emission_burn_fil | Total FIL burned minus emission burn.
-- asset.column = unattributed_burn_fil | Non-emission FIL burned minus message burn, message penalties, and cron burn. Includes contract burns and unclassified penalties. Null when any component is unknown.

-- asset.not_null = date
-- asset.unique = date

with activity as (
    select
        date,
        sum(gas_used_millions) as gas_used_millions,
        sum(transactions) as transactions,
        cast(sum(total_value_fil) as double) as total_value_fil,
        cast(sum(total_gas_fee_fil) as double) as total_gas_fee_fil,
        cast(sum(base_fee_burn_fil) as double) as base_fee_burn_fil,
        cast(sum(overestimation_burn_fil) as double) as overestimation_burn_fil,
        cast(sum(message_burn_fil) as double) as message_burn_fil,
        cast(sum(miner_tip_fil) as double) as miner_tip_fil,
        cast(sum(message_storage_provider_penalty_fil) as double)
            as message_storage_provider_penalty_fil,
        cast(sum(total_value_fil) + sum(total_gas_fee_fil) as double)
            as total_value_flow_fil
    from raw.lily_daily_network_activity_by_method
    group by 1
), emission_burn as (
    -- Solstice (FIP-0118) activated on 2026-10-19; earlier days have no emission burn.
    select
        dates.date,
        case
            when dates.date < date '2026-10-19' then 0
            when block_rewards.unobservable_tipsets = 0
                then block_rewards.burn_rewards_fil
        end as emission_burn_fil
    from raw.lily_daily_network_burn as dates
    left join model.network_daily_block_rewards as block_rewards
        using (date)
)
select
    date,
    activity.gas_used_millions,
    activity.transactions,
    activity.total_value_fil,
    activity.total_gas_fee_fil,
    activity.base_fee_burn_fil,
    activity.overestimation_burn_fil,
    activity.message_burn_fil,
    activity.miner_tip_fil,
    activity.message_storage_provider_penalty_fil,
    activity.total_value_flow_fil,
    cron_fees.storage_provider_cron_burn_fil,
    cron_fees.storage_provider_cron_fee_assessed_fil,
    cron_fees.storage_provider_cron_penalty_assessed_fil,
    network_burn.total_burn_fil,
    emission_burn.emission_burn_fil,
    network_burn.total_burn_fil - emission_burn.emission_burn_fil
        as non_emission_burn_fil,
    network_burn.total_burn_fil
        - emission_burn.emission_burn_fil
        - activity.message_burn_fil
        - activity.message_storage_provider_penalty_fil
        - cron_fees.storage_provider_cron_burn_fil
        as unattributed_burn_fil
from activity
full outer join raw.lily_daily_network_burn as network_burn
    using (date)
full outer join raw.lily_daily_miner_cron_fees as cron_fees
    using (date)
left join emission_burn
    using (date)
where date < cast(timezone('UTC', now()) as date)
order by date desc
