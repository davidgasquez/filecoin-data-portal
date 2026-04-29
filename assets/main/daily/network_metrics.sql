-- asset.description = Daily network core metrics.

-- asset.depends = model.daily_network_activity
-- asset.depends = model.daily_sector_lifecycle
-- asset.depends = model.daily_verified_claims
-- asset.depends = model.daily_filecoin_pay_activity
-- asset.depends = model.daily_filecoin_pay_arr
-- asset.depends = model.warm_storage_daily_activity
-- asset.depends = model.network_block_rewards_by_height
-- asset.depends = raw.coincodex_filecoin_market_data
-- asset.depends = raw.daily_network_power
-- asset.depends = raw.daily_network_economics
-- asset.depends = raw.daily_protocol_revenue

-- asset.column = date | UTC date.
-- asset.column = transactions | Onchain transactions.
-- asset.column = onboarded_pibs | Raw sector data onboarded on the date, in pebibytes.
-- asset.column = terminated_pibs | Raw sector data terminated on the date, in pebibytes.
-- asset.column = expired_pibs | Raw sector data expired on the date, in pebibytes.
-- asset.column = removed_pibs | Raw sector data removed on the date, in pebibytes.
-- asset.column = raw_power_pibs | End-of-day raw byte power, in pebibytes.
-- asset.column = quality_adjusted_power_pibs | End-of-day quality adjusted power, in pebibytes.
-- asset.column = gas_used_millions | Total gas used, in millions.
-- asset.column = total_value_fil | FIL transferred by top-level messages.
-- asset.column = total_gas_fee_fil | FIL paid in gas fees.
-- asset.column = base_fee_burn_fil | FIL burned by message base fees.
-- asset.column = base_fee_burn_usd | FIL burned by message base fees, valued with the daily average FIL price, in USD.
-- asset.column = message_burn_fil | FIL burned by message execution.
-- asset.column = message_burn_usd | FIL burned by message execution, valued with the daily average FIL price, in USD.
-- asset.column = total_value_flow_fil | FIL value transferred plus gas fees.
-- asset.column = protocol_revenue_fil | Daily total FIL burned on-chain, in FIL.
-- asset.column = protocol_revenue_usd | Daily total FIL burned on-chain, valued with the daily average FIL price, in USD.
-- asset.column = circulating_fil | End-of-day VM circulating supply, in FIL.
-- asset.column = mined_fil | End-of-day cumulative mined FIL, in FIL.
-- asset.column = vested_fil | End-of-day cumulative vested FIL, in FIL.
-- asset.column = locked_fil | End-of-day VM locked FIL, in FIL.
-- asset.column = burnt_fil | End-of-day cumulative burnt FIL, in FIL.
-- asset.column = pledge_collateral_fil | End-of-day total pledge collateral locked by storage providers, in FIL.
-- asset.column = filecoin_pay_active_payers | Payers with at least one active Filecoin Pay rail at end of day.
-- asset.column = filecoin_pay_active_rails | Active Filecoin Pay rails at end of day.
-- asset.column = usdfc_paid | Gross USDFC paid through Filecoin Pay rails on the date.
-- asset.column = active_payers | Payers with at least one active chargeable warm storage dataset.
-- asset.column = active_datasets | Active chargeable warm storage datasets.
-- asset.column = new_payers | Payers whose first chargeable warm storage dataset started billing on the date.
-- asset.column = new_datasets | Warm storage datasets whose billing started on the date.
-- asset.column = arr_usdfc | End-of-day ARR run-rate from active ARR-eligible rails.
-- asset.column = fil_token_price_avg_usd | Average FIL price in USD.
-- asset.column = fil_token_volume_usd | FIL trading volume in USD.
-- asset.column = fil_token_market_cap_usd | FIL market capitalization in USD.
-- asset.column = verified_data_onboarded_pibs | Verified data claimed on the date, in pebibytes.
-- asset.column = verified_claims | Successful verified claims on the date.
-- asset.column = verified_clients | Clients with at least one successful verified claim on the date.
-- asset.column = verified_providers | Providers with at least one successful verified claim on the date.
-- asset.column = blocks_mined | Block headers mined on the date.
-- asset.column = win_count | Winning proofs recorded on the date.
-- asset.column = block_rewards_fil | Exact block rewards minted on the date, in FIL.
-- asset.column = block_rewards_usd | Exact block rewards minted on the date, valued with the daily average FIL price, in USD.
-- asset.column = block_rewards_fil_per_qap_tib_day | Exact block rewards minted on the date per 1 TiB of network quality adjusted power, in FIL.
-- asset.column = block_rewards_usd_per_qap_tib_day | Exact block rewards minted on the date per 1 TiB of network quality adjusted power, in USD.
-- asset.column = reward_per_wincount_fil | Exact reward allocated per win count on the date, in FIL.

-- asset.not_null = date
-- asset.unique = date

with verified_claims as (
    select
        date,
        sum(verified_data_onboarded_tibs) / 1024 as verified_data_onboarded_pibs,
        sum(verified_claims) as verified_claims,
        count(distinct client_id) as verified_clients,
        count(distinct provider_id) as verified_providers
    from model.daily_verified_claims
    group by 1
), block_rewards as (
    select
        date,
        sum(blocks_mined) as blocks_mined,
        sum(network_win_count) as win_count,
        sum(block_rewards_fil) as block_rewards_fil,
        sum(block_rewards_fil) / nullif(sum(network_win_count), 0)
            as reward_per_wincount_fil
    from model.network_block_rewards_by_height
    group by 1
), market_data as (
    select
        cast(time_start as date) as date,
        price_avg_usd as fil_token_price_avg_usd,
        volume_usd as fil_token_volume_usd,
        market_cap_usd as fil_token_market_cap_usd
    from raw.coincodex_filecoin_market_data
), source_dates as (
    select date from model.warm_storage_daily_activity
    union
    select date from model.daily_filecoin_pay_activity
    union
    select date from model.daily_filecoin_pay_arr
    union
    select date from verified_claims
    union
    select date from block_rewards
    union
    select date from market_data
    union
    select date from raw.daily_protocol_revenue
    union
    select date from raw.daily_network_economics
    union
    select date from model.daily_sector_lifecycle
    union
    select date from model.daily_network_activity
    union
    select date from raw.daily_network_power
), date_bounds as (
    select
        min(date) as min_date,
        least(max(date), current_date - 1) as max_date
    from source_dates
), dates as (
    select cast(generate_series as date) as date
    from generate_series(
        (select min_date from date_bounds),
        (select max_date from date_bounds),
        interval 1 day
    )
)
select
    dates.date,
    coalesce(network_activity.transactions, 0) as transactions,
    coalesce(sector_lifecycle.onboarded_pibs, 0) as onboarded_pibs,
    coalesce(sector_lifecycle.terminated_pibs, 0) as terminated_pibs,
    coalesce(sector_lifecycle.expired_pibs, 0) as expired_pibs,
    coalesce(sector_lifecycle.removed_pibs, 0) as removed_pibs,
    network_power.raw_power_pibs,
    network_power.quality_adjusted_power_pibs,
    coalesce(network_activity.gas_used_millions, 0) as gas_used_millions,
    coalesce(network_activity.total_value_fil, 0) as total_value_fil,
    coalesce(network_activity.total_gas_fee_fil, 0) as total_gas_fee_fil,
    coalesce(network_activity.base_fee_burn_fil, 0) as base_fee_burn_fil,
    coalesce(network_activity.base_fee_burn_fil, 0)
        * market_data.fil_token_price_avg_usd as base_fee_burn_usd,
    coalesce(network_activity.message_burn_fil, 0) as message_burn_fil,
    coalesce(network_activity.message_burn_fil, 0)
        * market_data.fil_token_price_avg_usd as message_burn_usd,
    coalesce(network_activity.total_value_flow_fil, 0) as total_value_flow_fil,
    coalesce(protocol_revenue.protocol_revenue_fil, 0) as protocol_revenue_fil,
    coalesce(protocol_revenue.protocol_revenue_fil, 0)
        * market_data.fil_token_price_avg_usd as protocol_revenue_usd,
    coalesce(network_economics.circulating_fil, 0) as circulating_fil,
    coalesce(network_economics.mined_fil, 0) as mined_fil,
    coalesce(network_economics.vested_fil, 0) as vested_fil,
    coalesce(network_economics.locked_fil, 0) as locked_fil,
    coalesce(network_economics.burnt_fil, 0) as burnt_fil,
    coalesce(network_economics.pledge_collateral_fil, 0)
        as pledge_collateral_fil,
    coalesce(pay_activity.active_payers, 0) as filecoin_pay_active_payers,
    coalesce(pay_activity.active_rails, 0) as filecoin_pay_active_rails,
    coalesce(pay_activity.usdfc_paid, 0) as usdfc_paid,
    coalesce(warm_storage.active_payers, 0) as active_payers,
    coalesce(warm_storage.active_datasets, 0) as active_datasets,
    coalesce(warm_storage.new_payers, 0) as new_payers,
    coalesce(warm_storage.new_datasets, 0) as new_datasets,
    coalesce(pay_arr.arr_usdfc, 0) as arr_usdfc,
    market_data.fil_token_price_avg_usd,
    market_data.fil_token_volume_usd,
    market_data.fil_token_market_cap_usd,
    coalesce(verified_claims.verified_data_onboarded_pibs, 0)
        as verified_data_onboarded_pibs,
    coalesce(verified_claims.verified_claims, 0) as verified_claims,
    coalesce(verified_claims.verified_clients, 0) as verified_clients,
    coalesce(verified_claims.verified_providers, 0) as verified_providers,
    coalesce(block_rewards.blocks_mined, 0) as blocks_mined,
    coalesce(block_rewards.win_count, 0) as win_count,
    coalesce(block_rewards.block_rewards_fil, 0) as block_rewards_fil,
    coalesce(block_rewards.block_rewards_fil, 0) * market_data.fil_token_price_avg_usd
        as block_rewards_usd,
    coalesce(block_rewards.block_rewards_fil, 0)
        / nullif(network_power.quality_adjusted_power_pibs * 1024, 0)
        as block_rewards_fil_per_qap_tib_day,
    coalesce(block_rewards.block_rewards_fil, 0) * market_data.fil_token_price_avg_usd
        / nullif(network_power.quality_adjusted_power_pibs * 1024, 0)
        as block_rewards_usd_per_qap_tib_day,
    coalesce(block_rewards.reward_per_wincount_fil, 0) as reward_per_wincount_fil
from dates
left join model.warm_storage_daily_activity as warm_storage
    using (date)
left join model.daily_filecoin_pay_activity as pay_activity
    using (date)
left join model.daily_filecoin_pay_arr as pay_arr
    using (date)
left join market_data
    using (date)
left join raw.daily_protocol_revenue as protocol_revenue
    using (date)
left join raw.daily_network_economics as network_economics
    using (date)
left join verified_claims
    using (date)
left join block_rewards
    using (date)
left join model.daily_sector_lifecycle as sector_lifecycle
    using (date)
left join raw.daily_network_power as network_power
    using (date)
left join model.daily_network_activity as network_activity
    using (date)
order by date desc
