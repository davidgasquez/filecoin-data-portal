-- asset.description = Daily Filecoin Pay payment run-rate snapshots.

-- asset.depends = model.fevm_daily_checkpoints
-- asset.depends = model.filecoin_pay_rail_rate_intervals

-- asset.column = date | UTC date.
-- asset.column = filecoin_pay_gross_payment_volume_run_rate_usd | End-of-day annualized gross stablecoin payment volume run-rate from active eligible recurring Filecoin Pay rails.
-- asset.column = filecoin_pay_gross_payment_volume_run_rate_usdfc_usd | End-of-day annualized gross USDFC payment volume run-rate from active eligible recurring Filecoin Pay rails.
-- asset.column = filecoin_pay_gross_payment_volume_run_rate_usdc_axl_usd | End-of-day annualized gross USDC.axl payment volume run-rate from active eligible recurring Filecoin Pay rails.
-- asset.column = filecoin_pay_network_fee_arr_usd | End-of-day annualized Filecoin Pay network fee revenue from active eligible recurring stablecoin rails.

-- asset.not_null = date
-- asset.not_null = filecoin_pay_gross_payment_volume_run_rate_usd
-- asset.not_null = filecoin_pay_gross_payment_volume_run_rate_usdfc_usd
-- asset.not_null = filecoin_pay_gross_payment_volume_run_rate_usdc_axl_usd
-- asset.not_null = filecoin_pay_network_fee_arr_usd
-- asset.unique = date

with days as (
    select date, checkpoint_ordinal
    from model.fevm_daily_checkpoints
    where date >= (
        select coalesce(min(date(start_at)), min(date))
        from model.fevm_daily_checkpoints, model.filecoin_pay_rail_rate_intervals
    )
), daily_rates as (
    select
        days.date,
        coalesce(sum(intervals.rate_token_per_epoch), 0) as stablecoin_rate_per_epoch,
        coalesce(
            sum(case when intervals.token_symbol = 'USDFC' then intervals.rate_token_per_epoch else 0 end),
            0
        ) as usdfc_rate_per_epoch,
        coalesce(
            sum(case when intervals.token_symbol = 'USDC.axl' then intervals.rate_token_per_epoch else 0 end),
            0
        ) as usdc_axl_rate_per_epoch
    from days
    left join model.filecoin_pay_rail_rate_intervals as intervals
        on intervals.is_arr_eligible
       and intervals.is_stablecoin
       and intervals.rate_wei_per_epoch > 0
       and intervals.start_ordinal <= days.checkpoint_ordinal
       and coalesce(intervals.end_ordinal, 9223372036854775807) > days.checkpoint_ordinal
    group by 1
)
select
    date,
    stablecoin_rate_per_epoch * 2880 * 365 as filecoin_pay_gross_payment_volume_run_rate_usd,
    usdfc_rate_per_epoch * 2880 * 365 as filecoin_pay_gross_payment_volume_run_rate_usdfc_usd,
    usdc_axl_rate_per_epoch * 2880 * 365 as filecoin_pay_gross_payment_volume_run_rate_usdc_axl_usd,
    stablecoin_rate_per_epoch * 2880 * 365 * 0.005 as filecoin_pay_network_fee_arr_usd
from daily_rates
order by date desc
