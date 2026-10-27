-- asset.description = Filecoin Pay rail rate intervals. Terminated rails keep streaming until their end epoch.

-- asset.depends = model.pay_rails
-- asset.depends = raw.riba_eth_logs_decoded

-- asset.column = rail_id | Filecoin Pay rail identifier.
-- asset.column = service | Service classification.
-- asset.column = payer | Payer address.
-- asset.column = payee | Payee address.
-- asset.column = token | ERC20 token address.
-- asset.column = token_symbol | ERC20 token symbol.
-- asset.column = token_decimals | ERC20 token decimals.
-- asset.column = is_stablecoin | Whether the rail token is a tagged stablecoin.
-- asset.column = operator | Operator address.
-- asset.column = validator | Validator address.
-- asset.column = is_arr_eligible | Whether the rail counts toward recurring run-rate (tagged stablecoin, non-Dealbot payer).
-- asset.column = start_block | Inclusive start block.
-- asset.column = start_log_index | Inclusive start log index.
-- asset.column = start_ordinal | Inclusive event ordinal.
-- asset.column = start_at | UTC start timestamp.
-- asset.column = end_block | Exclusive end block, if any.
-- asset.column = end_log_index | Exclusive end log index, if any.
-- asset.column = end_ordinal | Exclusive end ordinal, if any.
-- asset.column = end_at | UTC end timestamp, if any.
-- asset.column = rate_wei_per_epoch | Recurring payment rate, in token wei per epoch.
-- asset.column = rate_token_per_epoch | Recurring payment rate, in whole-token units per epoch.

-- asset.not_null = rail_id

with params as (
    select 1598306400 as genesis_timestamp
),
rate_change_points as (
    select
        rails.rail_id,
        rails.created_block as block_number,
        rails.created_log_index as log_index,
        rails.created_block * 1000000 + rails.created_log_index as ordinal,
        cast(0 as decimal(38, 0)) as rate_wei_per_epoch
    from model.pay_rails as rails

    union all

    select
        cast(json_extract_string(events.args, '$.railId') as bigint) as rail_id,
        events.block_number,
        events.log_index,
        events.block_number * 1000000 + events.log_index as ordinal,
        cast(json_extract_string(events.args, '$.newRate') as decimal(38, 0)) as rate_wei_per_epoch
    from raw.riba_eth_logs_decoded as events
    where events.contract_name = 'filecoin_pay_v1'
      and events.event_name = 'RailRateModified'
),
valid_change_points as (
    select
        change_points.rail_id,
        change_points.block_number,
        change_points.log_index,
        change_points.ordinal,
        change_points.rate_wei_per_epoch,
        rails.service,
        rails.payer,
        rails.payee,
        rails.token,
        rails.token_symbol,
        rails.token_decimals,
        rails.is_stablecoin,
        rails.operator,
        rails.validator,
        rails.is_arr_eligible,
        rails.rail_end_ordinal
    from rate_change_points as change_points
    join (
        select
            *,
            -- Never before the termination itself, so snapshots taken before it stay unchanged
            greatest(
                terminated_block * 1000000 + terminated_log_index,
                terminated_end_epoch * 1000000
            ) as rail_end_ordinal
        from model.pay_rails
    ) as rails using (rail_id)
    where rails.rail_end_ordinal is null
       or change_points.ordinal < rails.rail_end_ordinal
),
ordered_intervals as (
    select
        rail_id,
        service,
        payer,
        payee,
        token,
        token_symbol,
        token_decimals,
        is_stablecoin,
        operator,
        validator,
        is_arr_eligible,
        block_number as start_block,
        log_index as start_log_index,
        ordinal as start_ordinal,
        lead(ordinal) over (partition by rail_id order by ordinal) as next_ordinal,
        rail_end_ordinal,
        rate_wei_per_epoch
    from valid_change_points
),
intervals as (
    select
        rail_id,
        service,
        payer,
        payee,
        token,
        token_symbol,
        token_decimals,
        is_stablecoin,
        operator,
        validator,
        is_arr_eligible,
        start_block,
        start_log_index,
        start_ordinal,
        coalesce(next_ordinal, rail_end_ordinal) as end_ordinal,
        rate_wei_per_epoch
    from ordered_intervals
)
select
    rail_id,
    service,
    payer,
    payee,
    token,
    token_symbol,
    token_decimals,
    is_stablecoin,
    operator,
    validator,
    is_arr_eligible,
    start_block,
    start_log_index,
    start_ordinal,
    to_timestamp(start_block * 30 + (select genesis_timestamp from params)) as start_at,
    case
        when end_ordinal is null then null
        else cast(end_ordinal / 1000000 as bigint)
    end as end_block,
    case
        when end_ordinal is null then null
        else cast(end_ordinal % 1000000 as bigint)
    end as end_log_index,
    end_ordinal,
    case
        when end_ordinal is null then null
        else to_timestamp(cast(end_ordinal / 1000000 as bigint) * 30 + (select genesis_timestamp from params))
    end as end_at,
    rate_wei_per_epoch,
    rate_wei_per_epoch / power(cast(10 as decimal(38, 0)), token_decimals) as rate_token_per_epoch
from intervals
order by start_at desc
