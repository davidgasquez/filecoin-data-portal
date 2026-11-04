-- asset.description = Sparse end-of-day rail rate change points.

-- asset.depends = model.pay_rail_rate_intervals
-- asset.depends = model.network_daily_fevm_checkpoints

-- asset.not_null = date
-- asset.not_null = rail_id
-- asset.not_null = rate_wei_per_epoch
-- asset.assert = rate_wei_per_epoch >= 0

with events as (
    select rail_id, start_ordinal as ordinal, rate_wei_per_epoch
    from model.pay_rail_rate_intervals
    union all
    select i.rail_id, i.end_ordinal, cast(0 as decimal(38, 0))
    from model.pay_rail_rate_intervals as i
    anti join model.pay_rail_rate_intervals as n
        on n.rail_id = i.rail_id and n.start_ordinal = i.end_ordinal
    where i.end_ordinal is not null
),
checkpoints as (
    select checkpoint_ordinal, min(date) as date
    from model.network_daily_fevm_checkpoints
    where date < current_date
    group by 1
),
daily as (
    select events.rail_id, checkpoints.date,
        cast(arg_max(events.rate_wei_per_epoch, events.ordinal) as decimal(38, 0)) as rate_wei_per_epoch
    from events
    asof join checkpoints on checkpoints.checkpoint_ordinal >= events.ordinal
    group by 1, 2
)
select date, rail_id, rate_wei_per_epoch
from daily
qualify rate_wei_per_epoch is distinct from lag(rate_wei_per_epoch) over (partition by rail_id order by date)
order by date desc, rail_id
