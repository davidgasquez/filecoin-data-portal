-- asset.description = Daily end-of-day Filecoin Pay operator metrics from active rail snapshots, with sparse operator-day rows.

-- asset.depends = main.foc_filecoin_pay_rail_rate_intervals
-- asset.depends = raw.fevm_eth_logs_decoded

-- asset.column = date | UTC day for the operator metrics snapshot.
-- asset.column = operator | Filecoin Pay operator address.
-- asset.column = active_rails | Distinct active rails managed by the operator at the end of the day.
-- asset.column = active_recurring_rails | Distinct active rails with a positive recurring payment rate at the end of the day.
-- asset.column = active_arr_eligible_rails | Distinct active recurring rails counted toward USDFC ARR at the end of the day.
-- asset.column = unique_payers | Distinct payer wallets across the operator's active rails at the end of the day.
-- asset.column = unique_payees | Distinct payee wallets across the operator's active rails at the end of the day.
-- asset.column = total_arr_usdfc | End-of-day USDFC ARR run-rate from the operator's active ARR-eligible recurring rails.

-- asset.not_null = date
-- asset.not_null = operator
-- asset.not_null = active_rails
-- asset.not_null = active_recurring_rails
-- asset.not_null = active_arr_eligible_rails
-- asset.not_null = unique_payers
-- asset.not_null = unique_payees
-- asset.not_null = total_arr_usdfc
-- asset.assert = active_rails > 0
-- asset.assert = active_recurring_rails >= 0
-- asset.assert = active_arr_eligible_rails >= 0
-- asset.assert = unique_payers > 0
-- asset.assert = unique_payees > 0
-- asset.assert = total_arr_usdfc >= 0

with params as (
    select 1598306400 as genesis_timestamp
),
latest_chain_day as (
    select max(date(to_timestamp(block_number * 30 + (select genesis_timestamp from params)))) as latest_observed_date
    from raw.fevm_eth_logs_decoded
),
days as (
    select cast(generate_series as date) as day
    from generate_series(
        coalesce(
            (select min(start_date) from main.foc_filecoin_pay_rail_rate_intervals),
            (select latest_observed_date from latest_chain_day)
        ),
        (select latest_observed_date from latest_chain_day),
        interval 1 day
    )
),
chain_day_ordinals as (
    select
        date(to_timestamp(block_number * 30 + (select genesis_timestamp from params))) as date,
        max(block_number * 1000000 + log_index) as day_end_ordinal
    from raw.fevm_eth_logs_decoded
    group by 1
),
daily_chain_checkpoints as (
    select
        days.day as date,
        max(chain_day_ordinals.day_end_ordinal) over (
            order by days.day
            rows between unbounded preceding and current row
        ) as checkpoint_ordinal
    from days
    left join chain_day_ordinals
        on days.day = chain_day_ordinals.date
),
operator_day_active_rails as (
    select
        checkpoints.date,
        intervals.operator,
        intervals.rail_id,
        intervals.payer,
        intervals.payee,
        intervals.is_arr_eligible,
        intervals.rate_wei_per_epoch,
        intervals.rate_token_per_epoch
    from daily_chain_checkpoints as checkpoints
    join main.foc_filecoin_pay_rail_rate_intervals as intervals
        on intervals.start_ordinal <= checkpoints.checkpoint_ordinal
       and coalesce(intervals.end_ordinal, 9223372036854775807) > checkpoints.checkpoint_ordinal
),
operator_days as (
    select distinct
        date,
        operator
    from operator_day_active_rails
),
operator_day_counter_metrics as (
    select
        date,
        operator,
        count(distinct rail_id) as active_rails,
        count(distinct case when rate_wei_per_epoch > 0 then rail_id end) as active_recurring_rails,
        count(distinct case when is_arr_eligible and rate_wei_per_epoch > 0 then rail_id end) as active_arr_eligible_rails,
        count(distinct payer) as unique_payers,
        count(distinct payee) as unique_payees
    from operator_day_active_rails
    group by 1, 2
),
operator_day_arr_metrics as (
    select
        date,
        operator,
        coalesce(sum(case when is_arr_eligible and rate_wei_per_epoch > 0 then rate_token_per_epoch else 0 end), 0)
            * 2880 * 365 as total_arr_usdfc
    from operator_day_active_rails
    group by 1, 2
)
select
    operator_days.date,
    operator_days.operator,
    counter_metrics.active_rails,
    counter_metrics.active_recurring_rails,
    counter_metrics.active_arr_eligible_rails,
    counter_metrics.unique_payers,
    counter_metrics.unique_payees,
    arr_metrics.total_arr_usdfc
from operator_days
join operator_day_counter_metrics as counter_metrics
    using (date, operator)
join operator_day_arr_metrics as arr_metrics
    using (date, operator)
order by date desc, operator
