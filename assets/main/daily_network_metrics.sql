-- asset.description = Daily network core metrics.

-- asset.depends = model.network_daily_activity
-- asset.depends = model.network_daily_sector_lifecycle
-- asset.depends = model.pay_daily_activity
-- asset.depends = model.pay_daily_payment_run_rate
-- asset.depends = model.foc_daily_storage_activity
-- asset.depends = model.foc_daily_storage_data
-- asset.depends = model.network_daily_miner_power
-- asset.depends = model.network_daily_block_rewards
-- asset.depends = raw.coincodex_market_data
-- asset.depends = raw.lily_daily_network_power
-- asset.depends = raw.lily_daily_network_economics
-- asset.depends = raw.oso_pgf_deployments
-- asset.depends = model.defi_daily_metrics

-- asset.column = date | UTC date.
-- asset.column = transactions | Onchain transactions.
-- asset.column = onboarded_pibs | Raw sector data onboarded on the date, in pebibytes.
-- asset.column = terminated_pibs | Raw sector data terminated on the date, in pebibytes.
-- asset.column = expired_pibs | Raw sector data expired on the date, in pebibytes.
-- asset.column = removed_pibs | Raw sector data removed on the date, in pebibytes.
-- asset.column = raw_power_pibs | End-of-day raw byte power, in pebibytes.
-- asset.column = quality_adjusted_power_pibs | End-of-day quality adjusted power, in pebibytes.
-- asset.column = storage_providers_with_power | Storage providers with positive end-of-day power.
-- asset.column = gas_used_millions | Total gas used, in millions.
-- asset.column = total_value_fil | FIL transferred by top-level messages.
-- asset.column = total_gas_fee_fil | FIL paid in gas fees.
-- asset.column = base_fee_burn_fil | FIL burned by message base fees.
-- asset.column = base_fee_burn_usd | FIL burned by message base fees, valued with the daily average FIL price, in USD.
-- asset.column = overestimation_burn_fil | FIL burned by gas overestimation.
-- asset.column = overestimation_burn_usd | FIL burned by gas overestimation, valued with the daily average FIL price, in USD.
-- asset.column = message_burn_fil | FIL burned by message execution.
-- asset.column = message_burn_usd | FIL burned by message execution, valued with the daily average FIL price, in USD.
-- asset.column = miner_tip_fil | FIL paid to miners as message tips.
-- asset.column = miner_tip_usd | FIL paid to miners as message tips, valued with the daily average FIL price, in USD.
-- asset.column = message_storage_provider_penalty_fil | FIL penalties incurred by storage providers during message execution.
-- asset.column = message_storage_provider_penalty_usd | FIL penalties incurred by storage providers during message execution, valued with the daily average FIL price, in USD.
-- asset.column = total_value_flow_fil | FIL value transferred plus gas fees.
-- asset.column = storage_provider_cron_burn_fil | FIL burned during storage provider cron events.
-- asset.column = storage_provider_cron_burn_usd | FIL burned during storage provider cron events, valued with the daily average FIL price, in USD.
-- asset.column = storage_provider_cron_fee_assessed_fil | FIL fees assessed during storage provider cron events, not necessarily burned.
-- asset.column = storage_provider_cron_penalty_assessed_fil | FIL penalties assessed during storage provider cron events, not necessarily burned.
-- asset.column = unattributed_burn_fil | Non-emission FIL burned minus message burn, message penalties, and cron burn. Includes contract burns and unclassified penalties.
-- asset.column = unattributed_burn_usd | Unattributed FIL burned, valued with the daily average FIL price, in USD.
-- asset.column = total_burn_fil | Total FIL burned on-chain, including emission burn. Null until the next day snapshot exists.
-- asset.column = total_burn_usd | Total FIL burned on-chain, valued with the daily average FIL price, in USD.
-- asset.column = emission_burn_fil | Newly minted block reward FIL burned as the FIP-0118 residual.
-- asset.column = emission_burn_usd | Emission burn, valued with the daily average FIL price, in USD.
-- asset.column = non_emission_burn_fil | Total FIL burned minus emission burn.
-- asset.column = non_emission_burn_usd | Non-emission FIL burned, valued with the daily average FIL price, in USD.
-- asset.column = circulating_fil | End-of-day VM circulating supply, in FIL.
-- asset.column = mined_fil | End-of-day cumulative mined FIL, in FIL.
-- asset.column = vested_fil | End-of-day cumulative vested FIL, in FIL.
-- asset.column = locked_fil | End-of-day VM locked FIL, in FIL.
-- asset.column = burnt_fil | End-of-day cumulative burned FIL, in FIL.
-- asset.column = pledge_collateral_fil | End-of-day total pledge collateral locked by storage providers, in FIL.
-- asset.column = filecoin_pay_active_payers | Payers with at least one unterminated Filecoin Pay rail at end of day, whether or not it is billing.
-- asset.column = filecoin_pay_active_rails | Unterminated Filecoin Pay rails at end of day, whether or not they are billing.
-- asset.column = filecoin_pay_active_operators | Operators with at least one unterminated Filecoin Pay rail at end of day.
-- asset.column = filecoin_pay_paid_usd | Gross stablecoin paid through Filecoin Pay rails on the date, assuming tagged stablecoins at $1.
-- asset.column = warm_storage_billing_payers | Payers with at least one warm storage data set billing at a positive PDP rail rate at end of day.
-- asset.column = warm_storage_billing_data_sets | Warm storage data sets billing at a positive PDP rail rate at end of day.
-- asset.column = warm_storage_new_billing_payers | Payers whose first warm storage data set started billing on the date.
-- asset.column = warm_storage_new_billing_data_sets | Warm storage data sets whose billing started on the date.
-- asset.column = warm_storage_stored_bytes | End-of-day raw payload bytes of pieces stored in warm storage datasets, counting every stored copy.
-- asset.column = filecoin_pay_gross_payment_volume_run_rate_usd | End-of-day annualized gross stablecoin payment volume run-rate from active eligible recurring Filecoin Pay rails.
-- asset.column = filecoin_pay_gross_payment_volume_run_rate_usdfc_usd | End-of-day annualized gross USDFC payment volume run-rate from active eligible recurring Filecoin Pay rails.
-- asset.column = filecoin_pay_gross_payment_volume_run_rate_usdc_axl_usd | End-of-day annualized gross USDC.axl payment volume run-rate from active eligible recurring Filecoin Pay rails.
-- asset.column = filecoin_pay_network_fee_arr_usd | End-of-day annualized Filecoin Pay network fee revenue from active eligible recurring stablecoin rails.
-- asset.column = fil_token_price_avg_usd | Average FIL price in USD.
-- asset.column = fil_token_volume_usd | FIL trading volume in USD.
-- asset.column = fil_token_market_cap_usd | FIL market capitalization in USD.
-- asset.column = defi_tvl_usd | DefiLlama Filecoin DeFi TVL, excluding liquid staking and double counted TVL, in USD. Snapshot dated by DefiLlama.
-- asset.column = defi_protocol_tvl_usd_json | DefiLlama Filecoin TVL by protocol slug, in USD, including liquid staking. Snapshot dated by DefiLlama.
-- asset.column = glif_tvl_fil | GLIF Filecoin TVL from DefiLlama, including borrower collateral, in FIL. Snapshot dated by DefiLlama.
-- asset.column = glif_tvl_usd | GLIF Filecoin TVL from DefiLlama, including borrower collateral, in USD. Snapshot dated by DefiLlama.
-- asset.column = glif_pool_assets_fil | End-of-day GLIF Infinity Pool total assets, in FIL.
-- asset.column = glif_borrowed_fil | End-of-day FIL borrowed from the GLIF Infinity Pool.
-- asset.column = glif_available_liquidity_fil | End-of-day FIL borrowable from the GLIF Infinity Pool.
-- asset.column = glif_utilization | End-of-day GLIF borrowed FIL divided by pool total assets.
-- asset.column = ifil_base_apy | GLIF iFIL annualized base yield from DefiLlama, as a fraction. Latest observation on the date.
-- asset.column = usdfc_supply | DefiLlama USDFC circulating supply, in tokens. Snapshot dated by DefiLlama.
-- asset.column = usdc_axl_supply | End-of-day axlUSDC total supply on Filecoin, in tokens.
-- asset.column = blocks_mined | Block headers mined on the date.
-- asset.column = win_count | Winning proofs recorded on the date.
-- asset.column = minted_rewards_fil | Block rewards minted on the date across miner, service, and emission burn allocations, in FIL. Null when any tipset reward is unobservable.
-- asset.column = minted_rewards_usd | Minted block rewards, valued with the daily average FIL price, in USD.
-- asset.column = miner_rewards_fil | Block rewards allocated to block-winning storage providers, excluding gas tips, in FIL. Null when any tipset reward is unobservable.
-- asset.column = miner_rewards_usd | Miner block rewards, valued with the daily average FIL price, in USD.
-- asset.column = service_rewards_fil | Block rewards accrued to the FIP-0118 service stream, in FIL. Null when any tipset reward is unobservable.
-- asset.column = service_rewards_usd | Service stream block rewards, valued with the daily average FIL price, in USD.
-- asset.column = mining_yield | Annualized miner block rewards divided by locked FIL.
-- asset.column = yearly_inflation_rate | Year-over-year circulating FIL change.
-- asset.column = miner_rewards_fil_per_qap_tib_day | Miner block rewards on the date per 1 TiB of network quality adjusted power, in FIL.
-- asset.column = miner_rewards_usd_per_qap_tib_day | Miner block rewards on the date per 1 TiB of network quality adjusted power, in USD.
-- asset.column = reward_per_wincount_fil | Miner block rewards per observable win count on the date, in FIL.
-- asset.column = annual_pgf_deployments_usd | Public goods funding deployments disbursed over the trailing 365 days, in USD.
-- asset.column = annual_non_emission_burn_usd | Non-emission FIL burned over the complete days of the trailing 365 days, in USD.
-- asset.column = annual_distributed_rewards_usd | Miner and service block rewards over the complete days of the trailing 365 days, in USD.
-- asset.column = annual_coverage_days | Complete days in the trailing 365 days, with known non-emission burn, miner rewards, service rewards, and FIL price.
-- asset.column = burn_coverage_ratio | Annual non-emission burn divided by annual public goods funding plus annual distributed rewards. Burn and rewards cover only complete days, while public goods funding covers all 365 days.

-- asset.not_null = date
-- asset.unique = date
-- asset.assert = abs(message_burn_fil - base_fee_burn_fil - overestimation_burn_fil) < 0.000001
-- asset.assert = abs(total_gas_fee_fil - base_fee_burn_fil - overestimation_burn_fil - miner_tip_fil) < 0.000001

with block_rewards as (
    select
        date,
        blocks_mined,
        win_count,
        if(unobservable_tipsets = 0, minted_rewards_fil, null) as minted_rewards_fil,
        if(unobservable_tipsets = 0, miner_rewards_fil, null) as miner_rewards_fil,
        if(unobservable_tipsets = 0, service_rewards_fil, null) as service_rewards_fil,
        reward_per_wincount_fil
    from model.network_daily_block_rewards
), market_data as (
    select
        cast(time_start as date) as date,
        price_avg_usd as fil_token_price_avg_usd,
        volume_usd as fil_token_volume_usd,
        market_cap_usd as fil_token_market_cap_usd
    from raw.coincodex_market_data
), storage_providers_with_power as (
    select
        date,
        count(distinct miner_id) as storage_providers_with_power
    from model.network_daily_miner_power
    where has_power
    group by 1
), source_dates as (
    select date from model.foc_daily_storage_activity
    union
    select date from model.foc_daily_storage_data
    union
    select date from model.pay_daily_activity
    union
    select date from model.pay_daily_payment_run_rate
    union
    select date from model.network_daily_block_rewards
    union
    select date from storage_providers_with_power
    union
    select date from market_data
    union
    select date from raw.lily_daily_network_economics
    union
    select date from model.network_daily_sector_lifecycle
    union
    select date from model.network_daily_activity
    union
    select date from raw.lily_daily_network_power
    union
    select date from model.defi_daily_metrics
), date_bounds as (
    select
        min(date) as min_date,
        least(max(date), cast(timezone('UTC', now()) as date) - 1) as max_date
    from source_dates
), dates as (
    select cast(generate_series as date) as date
    from generate_series(
        (select min_date from date_bounds),
        (select max_date from date_bounds),
        interval 1 day
    )
), pgf_deployments_by_date as (
    select
        dates.date,
        coalesce(sum(pgf_deployments.disbursed_usd), 0)
            as annual_pgf_deployments_usd
    from dates
    left join raw.oso_pgf_deployments as pgf_deployments
        on pgf_deployments.date between dates.date - interval 364 days
            and dates.date
    group by 1
), daily_metrics as (
select
    dates.date,
    network_activity.transactions as transactions,
    sector_lifecycle.onboarded_pibs as onboarded_pibs,
    sector_lifecycle.terminated_pibs as terminated_pibs,
    sector_lifecycle.expired_pibs as expired_pibs,
    sector_lifecycle.removed_pibs as removed_pibs,
    network_power.raw_power_pibs,
    network_power.quality_adjusted_power_pibs,
    storage_providers_with_power.storage_providers_with_power as storage_providers_with_power,
    network_activity.gas_used_millions as gas_used_millions,
    network_activity.total_value_fil as total_value_fil,
    network_activity.total_gas_fee_fil as total_gas_fee_fil,
    network_activity.base_fee_burn_fil as base_fee_burn_fil,
    network_activity.base_fee_burn_fil
        * market_data.fil_token_price_avg_usd as base_fee_burn_usd,
    network_activity.overestimation_burn_fil as overestimation_burn_fil,
    network_activity.overestimation_burn_fil
        * market_data.fil_token_price_avg_usd as overestimation_burn_usd,
    network_activity.message_burn_fil as message_burn_fil,
    network_activity.message_burn_fil
        * market_data.fil_token_price_avg_usd as message_burn_usd,
    network_activity.miner_tip_fil as miner_tip_fil,
    network_activity.miner_tip_fil
        * market_data.fil_token_price_avg_usd as miner_tip_usd,
    network_activity.message_storage_provider_penalty_fil
        as message_storage_provider_penalty_fil,
    network_activity.message_storage_provider_penalty_fil
        * market_data.fil_token_price_avg_usd
        as message_storage_provider_penalty_usd,
    network_activity.total_value_flow_fil as total_value_flow_fil,
    network_activity.storage_provider_cron_burn_fil
        as storage_provider_cron_burn_fil,
    network_activity.storage_provider_cron_burn_fil
        * market_data.fil_token_price_avg_usd as storage_provider_cron_burn_usd,
    network_activity.storage_provider_cron_fee_assessed_fil
        as storage_provider_cron_fee_assessed_fil,
    network_activity.storage_provider_cron_penalty_assessed_fil
        as storage_provider_cron_penalty_assessed_fil,
    network_activity.unattributed_burn_fil,
    network_activity.unattributed_burn_fil
        * market_data.fil_token_price_avg_usd as unattributed_burn_usd,
    network_activity.total_burn_fil,
    network_activity.total_burn_fil * market_data.fil_token_price_avg_usd
        as total_burn_usd,
    network_activity.emission_burn_fil,
    network_activity.emission_burn_fil * market_data.fil_token_price_avg_usd
        as emission_burn_usd,
    network_activity.non_emission_burn_fil,
    network_activity.non_emission_burn_fil * market_data.fil_token_price_avg_usd
        as non_emission_burn_usd,
    network_economics.circulating_fil as circulating_fil,
    network_economics.mined_fil as mined_fil,
    network_economics.vested_fil as vested_fil,
    network_economics.locked_fil as locked_fil,
    network_economics.burnt_fil as burnt_fil,
    network_economics.pledge_collateral_fil
        as pledge_collateral_fil,
    pay_activity.active_payers as filecoin_pay_active_payers,
    pay_activity.active_rails as filecoin_pay_active_rails,
    pay_activity.active_operators as filecoin_pay_active_operators,
    pay_activity.filecoin_pay_paid_usd as filecoin_pay_paid_usd,
    warm_storage.billing_payers as warm_storage_billing_payers,
    warm_storage.billing_data_sets as warm_storage_billing_data_sets,
    warm_storage.new_billing_payers as warm_storage_new_billing_payers,
    warm_storage.new_billing_data_sets as warm_storage_new_billing_data_sets,
    warm_storage_data.stored_bytes as warm_storage_stored_bytes,
    pay_run_rate.filecoin_pay_gross_payment_volume_run_rate_usd
        as filecoin_pay_gross_payment_volume_run_rate_usd,
    pay_run_rate.filecoin_pay_gross_payment_volume_run_rate_usdfc_usd
        as filecoin_pay_gross_payment_volume_run_rate_usdfc_usd,
    pay_run_rate.filecoin_pay_gross_payment_volume_run_rate_usdc_axl_usd
        as filecoin_pay_gross_payment_volume_run_rate_usdc_axl_usd,
    pay_run_rate.filecoin_pay_network_fee_arr_usd
        as filecoin_pay_network_fee_arr_usd,
    market_data.fil_token_price_avg_usd,
    market_data.fil_token_volume_usd,
    market_data.fil_token_market_cap_usd,
    defi.defi_tvl_usd,
    defi.defi_protocol_tvl_usd_json,
    defi.glif_tvl_fil,
    defi.glif_tvl_usd,
    defi.glif_pool_assets_fil,
    defi.glif_borrowed_fil,
    defi.glif_available_liquidity_fil,
    defi.glif_utilization,
    defi.ifil_base_apy,
    defi.usdfc_supply,
    defi.usdc_axl_supply,
    block_rewards.blocks_mined as blocks_mined,
    block_rewards.win_count as win_count,
    block_rewards.minted_rewards_fil,
    block_rewards.minted_rewards_fil * market_data.fil_token_price_avg_usd
        as minted_rewards_usd,
    block_rewards.miner_rewards_fil,
    block_rewards.miner_rewards_fil * market_data.fil_token_price_avg_usd
        as miner_rewards_usd,
    block_rewards.service_rewards_fil,
    block_rewards.service_rewards_fil * market_data.fil_token_price_avg_usd
        as service_rewards_usd,
    block_rewards.miner_rewards_fil
        / nullif(network_economics.locked_fil, 0) * 365 as mining_yield,
    block_rewards.miner_rewards_fil
        / nullif(network_power.quality_adjusted_power_pibs * 1024, 0)
        as miner_rewards_fil_per_qap_tib_day,
    block_rewards.miner_rewards_fil * market_data.fil_token_price_avg_usd
        / nullif(network_power.quality_adjusted_power_pibs * 1024, 0)
        as miner_rewards_usd_per_qap_tib_day,
    block_rewards.reward_per_wincount_fil,
    pgf_deployments.annual_pgf_deployments_usd
from dates
left join model.foc_daily_storage_activity as warm_storage
    using (date)
left join model.foc_daily_storage_data as warm_storage_data
    using (date)
left join model.pay_daily_activity as pay_activity
    using (date)
left join model.pay_daily_payment_run_rate as pay_run_rate
    using (date)
left join pgf_deployments_by_date as pgf_deployments
    using (date)
left join market_data
    using (date)
left join raw.lily_daily_network_economics as network_economics
    using (date)
left join block_rewards
    using (date)
left join model.network_daily_sector_lifecycle as sector_lifecycle
    using (date)
left join raw.lily_daily_network_power as network_power
    using (date)
left join storage_providers_with_power
    using (date)
left join model.network_daily_activity as network_activity
    using (date)
left join model.defi_daily_metrics as defi
    using (date)
), annual_metrics as (
    select
        *,
        (circulating_fil - lag(circulating_fil, 365) over (order by date))
            / nullif(lag(circulating_fil, 365) over (order by date), 0)
            as yearly_inflation_rate,
        sum(non_emission_burn_usd) filter (where coverage_complete) over annual_window
            as annual_non_emission_burn_usd,
        sum(miner_rewards_usd + service_rewards_usd)
            filter (where coverage_complete) over annual_window
            as annual_distributed_rewards_usd,
        count(*) filter (where coverage_complete) over annual_window
            as annual_coverage_days
    from (
        select
            *,
            non_emission_burn_usd is not null
                and miner_rewards_usd is not null
                and service_rewards_usd is not null as coverage_complete
        from daily_metrics
    )
    window annual_window as (
        order by date
        range between interval 364 days preceding and current row
    )
)
select
    * exclude (coverage_complete),
    annual_non_emission_burn_usd
        / nullif(annual_pgf_deployments_usd + annual_distributed_rewards_usd, 0)
        as burn_coverage_ratio
from annual_metrics
order by date desc
