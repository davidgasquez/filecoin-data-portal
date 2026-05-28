-- asset.description = Daily Filecoin Pay ARR snapshots.

-- asset.depends = model.fevm_daily_checkpoints
-- asset.depends = model.filecoin_pay_rail_rate_intervals

-- asset.column = date | UTC date.
-- asset.column = arr_filecoin_pay_usd | End-of-day USD ARR run-rate from active stablecoin recurring rails.

-- asset.not_null = date
-- asset.not_null = arr_filecoin_pay_usd
-- asset.unique = date

with days as (
    select date, checkpoint_ordinal
    from model.fevm_daily_checkpoints
    where date >= (
        select coalesce(min(date(start_at)), min(date))
        from model.fevm_daily_checkpoints, model.filecoin_pay_rail_rate_intervals
    )
)
select
    days.date,
    coalesce(sum(intervals.rate_token_per_epoch), 0) * 2880 * 365 as arr_filecoin_pay_usd
from days
left join model.filecoin_pay_rail_rate_intervals as intervals
    on intervals.is_arr_eligible
   and intervals.rate_wei_per_epoch > 0
   and intervals.start_ordinal <= days.checkpoint_ordinal
   and coalesce(intervals.end_ordinal, 9223372036854775807) > days.checkpoint_ordinal
group by 1
order by date desc
