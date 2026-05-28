-- asset.description = Daily Filecoin Pay activity snapshots.

-- asset.depends = model.fevm_daily_checkpoints
-- asset.depends = model.filecoin_pay_rails
-- asset.depends = raw.fevm_eth_logs_decoded

-- asset.column = date | UTC date.
-- asset.column = active_payers | Payers with at least one active rail at end of day.
-- asset.column = active_rails | Active rails at end of day.
-- asset.column = filecoin_pay_paid_usd | Gross stablecoin paid through Filecoin Pay rails on the date, assuming tagged stablecoins at $1.

-- asset.not_null = date
-- asset.not_null = active_payers
-- asset.not_null = active_rails
-- asset.not_null = filecoin_pay_paid_usd
-- asset.unique = date

with days as (
    select date, checkpoint_ordinal
    from model.fevm_daily_checkpoints
    where date >= coalesce(
        (select min(date(created_at)) from model.filecoin_pay_rails),
        (select min(date) from model.fevm_daily_checkpoints)
    )
), rails as (
    select
        rail_id,
        payer,
        created_block * 1000000 + created_log_index as created_ordinal,
        case
            when terminated_block is null then null
            else terminated_block * 1000000 + terminated_log_index
        end as terminated_ordinal
    from model.filecoin_pay_rails
), payment_events as (
    select
        events.file_date as date,
        case
            when events.event_name = 'RailSettled' then
                cast(json_extract_string(events.args, '$.totalSettledAmount') as decimal(38, 0))
            when events.event_name = 'RailOneTimePaymentProcessed' then
                cast(json_extract_string(events.args, '$.netPayeeAmount') as decimal(38, 0))
                + cast(json_extract_string(events.args, '$.operatorCommission') as decimal(38, 0))
                + cast(json_extract_string(events.args, '$.networkFee') as decimal(38, 0))
        end / power(cast(10 as decimal(38, 0)), payment_rails.token_decimals)
            as paid_usd
    from raw.fevm_eth_logs_decoded as events
    join model.filecoin_pay_rails as payment_rails
        on cast(json_extract_string(events.args, '$.railId') as bigint) = payment_rails.rail_id
    where events.abi_name = 'filecoin_pay_v1'
      and events.event_name in ('RailSettled', 'RailOneTimePaymentProcessed')
      and payment_rails.is_stablecoin
      and events.file_date <= current_date - 1
), daily_payments as (
    select
        date,
        sum(paid_usd) as filecoin_pay_paid_usd
    from payment_events
    group by 1
), active_counts as (
    select
        days.date,
        count(distinct rails.payer) as active_payers,
        count(distinct rails.rail_id) as active_rails
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
    coalesce(daily_payments.filecoin_pay_paid_usd, 0) as filecoin_pay_paid_usd
from active_counts
left join daily_payments using (date)
order by date desc
