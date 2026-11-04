-- Sparse history must reconstruct every covered end-of-day interval rate exactly.
with expected as (
    select c.date, i.rail_id, i.rate_wei_per_epoch
    from model.network_daily_fevm_checkpoints c
    join model.pay_rail_rate_intervals i
      on i.start_ordinal <= c.checkpoint_ordinal
     and coalesce(i.end_ordinal, 9223372036854775807) > c.checkpoint_ordinal
    where c.date < current_date
),
actual as (
    select c.date, r.rail_id, r.rate_wei_per_epoch
    from model.network_daily_fevm_checkpoints c
    cross join (select distinct rail_id from model.pay_daily_rail_rates) ids
    asof join model.pay_daily_rail_rates r on ids.rail_id = r.rail_id and c.date >= r.date
    where c.date < current_date
)
select coalesce(a.date, e.date) as date, coalesce(a.rail_id, e.rail_id) as rail_id
from actual a full join expected e using (date, rail_id)
where coalesce(a.rate_wei_per_epoch, 0) != coalesce(e.rate_wei_per_epoch, 0)
union all
select date, rail_id from model.pay_daily_rail_rates group by all having count(*) > 1
