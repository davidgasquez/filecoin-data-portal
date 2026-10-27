-- asset.description = Daily Filecoin Pay activity snapshots.

-- asset.depends = model.network_daily_fevm_checkpoints
-- asset.depends = model.pay_rails
-- asset.depends = model.pay_payments

-- asset.column = date | UTC date.
-- asset.column = active_payers | Payers with at least one active rail at end of day.
-- asset.column = active_rails | Active rails at end of day.
-- asset.column = active_operators | Operators with at least one unterminated rail at end of day.
-- asset.column = filecoin_pay_paid_usd | Gross stablecoin paid through Filecoin Pay rails on the date, assuming tagged stablecoins at $1.

-- asset.not_null = date
-- asset.not_null = active_payers
-- asset.not_null = active_rails
-- asset.not_null = active_operators
-- asset.not_null = filecoin_pay_paid_usd
-- asset.unique = date

with days as (
    select date, checkpoint_ordinal
    from model.network_daily_fevm_checkpoints
    where date >= coalesce(
        (select min(date(created_at)) from model.pay_rails),
        (select min(date) from model.network_daily_fevm_checkpoints)
    )
), rails as (
    select
        rail_id,
        payer,
        operator,
        created_block * 1000000 + created_log_index as created_ordinal,
        case
            when terminated_block is null then null
            else terminated_block * 1000000 + terminated_log_index
        end as terminated_ordinal
    from model.pay_rails
), daily_payments as (
    select
        date,
        sum(gross_amount_usd) as filecoin_pay_paid_usd
    from model.pay_payments
    where is_stablecoin
      and date < cast(timezone('UTC', now()) as date)
    group by 1
), active_counts as (
    select
        days.date,
        count(distinct rails.payer) as active_payers,
        count(distinct rails.rail_id) as active_rails,
        count(distinct rails.operator) as active_operators
    from days
    left join rails
        on rails.created_ordinal <= days.checkpoint_ordinal
       and coalesce(rails.terminated_ordinal, 9223372036854775807) > days.checkpoint_ordinal
    group by 1
)
select
    active_counts.date,
    active_counts.active_payers,
    active_counts.active_rails,
    active_counts.active_operators,
    coalesce(daily_payments.filecoin_pay_paid_usd, 0) as filecoin_pay_paid_usd
from active_counts
left join daily_payments using (date)
order by date desc
