-- asset.description = Daily Filecoin Pay activity snapshots.

-- asset.depends = model.fevm_daily_checkpoints
-- asset.depends = model.filecoin_pay_rails
-- asset.depends = raw.fevm_eth_logs_decoded

-- asset.column = date | UTC date.
-- asset.column = active_payers | Payers with at least one active rail at end of day.
-- asset.column = active_rails | Active rails at end of day.
-- asset.column = usdfc_paid | Gross USDFC paid through Filecoin Pay rails on the date.

-- asset.not_null = date
-- asset.not_null = active_payers
-- asset.not_null = active_rails
-- asset.not_null = usdfc_paid
-- asset.unique = date

with params as (
    select
        '0x80b98d3aa09ffff255c3ba4a241111ff1262f045' as usdfc_token,
        cast(1000000000000000000 as decimal(38, 0)) as token_scale
), days as (
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
        date(to_timestamp(events.block_number * 30 + 1598306400)) as date,
        case
            when events.event_name = 'RailSettled' then
                cast(json_extract_string(events.args, '$.totalSettledAmount') as decimal(38, 0))
            when events.event_name = 'RailOneTimePaymentProcessed' then
                cast(json_extract_string(events.args, '$.netPayeeAmount') as decimal(38, 0))
                + cast(json_extract_string(events.args, '$.operatorCommission') as decimal(38, 0))
                + cast(json_extract_string(events.args, '$.networkFee') as decimal(38, 0))
        end as paid_wei
    from raw.fevm_eth_logs_decoded as events
    join model.filecoin_pay_rails as payment_rails
        on cast(json_extract_string(events.args, '$.railId') as bigint) = payment_rails.rail_id
    where events.abi_name = 'filecoin_pay_v1'
      and events.event_name in ('RailSettled', 'RailOneTimePaymentProcessed')
      and payment_rails.token = (select usdfc_token from params)
), daily_payments as (
    select
        date,
        sum(paid_wei) / (select token_scale from params) as usdfc_paid
    from payment_events
    group by 1
)
select
    days.date,
    count(distinct rails.payer) as active_payers,
    count(distinct rails.rail_id) as active_rails,
    coalesce(daily_payments.usdfc_paid, 0) as usdfc_paid
from days
left join rails
    on rails.created_ordinal <= days.checkpoint_ordinal
   and coalesce(rails.terminated_ordinal, 9223372036854775807) > days.checkpoint_ordinal
left join daily_payments using (date)
group by 1, 4
order by date desc
