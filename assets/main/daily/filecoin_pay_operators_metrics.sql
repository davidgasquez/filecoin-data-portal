-- asset.description = Daily Filecoin Pay operators metrics.

-- asset.depends = model.fevm_daily_checkpoints
-- asset.depends = model.filecoin_pay_rail_rate_intervals

-- asset.column = date | UTC date.
-- asset.column = operator | Filecoin Pay operator address.
-- asset.column = active_rails | Active rails at end of day.
-- asset.column = recurring_rails | Active rails with a positive recurring rate at end of day.
-- asset.column = arr_eligible_rails | Active recurring rails counted toward ARR at end of day.
-- asset.column = unique_payers | Payers across the operator's active rails at end of day.
-- asset.column = unique_payees | Payees across the operator's active rails at end of day.
-- asset.column = arr_usdfc | End-of-day ARR run-rate from the operator's active ARR-eligible rails.

-- asset.not_null = date
-- asset.not_null = operator
-- asset.not_null = active_rails
-- asset.not_null = recurring_rails
-- asset.not_null = arr_eligible_rails
-- asset.not_null = unique_payers
-- asset.not_null = unique_payees
-- asset.not_null = arr_usdfc

with days as (
    select date, checkpoint_ordinal
    from model.fevm_daily_checkpoints
    where date >= (
        select coalesce(min(date(start_at)), min(date))
        from model.fevm_daily_checkpoints, model.filecoin_pay_rail_rate_intervals
    )
),
operator_day_active_rails as (
    select
        days.date,
        intervals.operator,
        intervals.rail_id,
        intervals.payer,
        intervals.payee,
        intervals.is_arr_eligible,
        intervals.rate_wei_per_epoch,
        intervals.rate_token_per_epoch
    from days
    join model.filecoin_pay_rail_rate_intervals as intervals
        on intervals.start_ordinal <= days.checkpoint_ordinal
       and coalesce(intervals.end_ordinal, 9223372036854775807) > days.checkpoint_ordinal
)
select
    date,
    operator,
    count(distinct rail_id) as active_rails,
    count(distinct case when rate_wei_per_epoch > 0 then rail_id end) as recurring_rails,
    count(distinct case when is_arr_eligible and rate_wei_per_epoch > 0 then rail_id end) as arr_eligible_rails,
    count(distinct payer) as unique_payers,
    count(distinct payee) as unique_payees,
    coalesce(sum(case when is_arr_eligible and rate_wei_per_epoch > 0 then rate_token_per_epoch else 0 end), 0)
        * 2880 * 365 as arr_usdfc
from operator_day_active_rails
group by 1, 2
order by date desc
