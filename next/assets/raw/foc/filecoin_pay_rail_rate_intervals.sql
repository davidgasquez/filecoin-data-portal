-- asset.description = Mainnet Filecoin Pay rail rate intervals reconstructed from onchain events. Each row is a half-open interval [start_ordinal, end_ordinal) where a rail's recurring payment rate is constant.

-- asset.depends = raw.foc_filecoin_pay_rails
-- asset.depends = raw.fevm_eth_logs_decoded

-- asset.column = rail_id | Filecoin Pay rail identifier.
-- asset.column = service | Service classification copied from raw.foc_filecoin_pay_rails.
-- asset.column = payer | Payer address funding the rail.
-- asset.column = payee | Payee address receiving the rail payments.
-- asset.column = token | ERC20 token address used by the rail.
-- asset.column = operator | Operator address recorded on rail creation.
-- asset.column = validator | Validator address recorded on rail creation.
-- asset.column = is_arr_eligible | Whether the rail should count toward USDFC ARR.
-- asset.column = start_block | Inclusive block where the interval starts.
-- asset.column = start_log_index | Inclusive log index where the interval starts.
-- asset.column = start_ordinal | Inclusive event ordinal computed as block_number * 1000000 + log_index.
-- asset.column = start_date | UTC date derived from the start block.
-- asset.column = end_block | Exclusive block where the interval ends, if any.
-- asset.column = end_log_index | Exclusive log index where the interval ends, if any.
-- asset.column = end_ordinal | Exclusive event ordinal where the interval ends, if any.
-- asset.column = end_date | UTC date derived from the end block, if any.
-- asset.column = rate_wei_per_epoch | Constant recurring payment rate during the interval, in token wei per epoch.
-- asset.column = rate_token_per_epoch | Constant recurring payment rate during the interval, scaled to whole-token units.

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
        cast(0 as bigint) as rate_wei_per_epoch
    from raw.foc_filecoin_pay_rails as rails

    union all

    select
        cast(json_extract_string(events.args, '$.railId') as bigint) as rail_id,
        events.block_number,
        events.log_index,
        events.block_number * 1000000 + events.log_index as ordinal,
        cast(json_extract_string(events.args, '$.newRate') as bigint) as rate_wei_per_epoch
    from raw.fevm_eth_logs_decoded as events
    where events.abi_name = 'filecoin_pay_v1'
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
        rails.operator,
        rails.validator,
        rails.is_arr_eligible,
        case
            when rails.terminated_block is null then null
            else rails.terminated_block * 1000000 + rails.terminated_log_index
        end as terminated_ordinal
    from rate_change_points as change_points
    join raw.foc_filecoin_pay_rails as rails using (rail_id)
    where rails.terminated_block is null
       or change_points.ordinal < rails.terminated_block * 1000000 + rails.terminated_log_index
),
ordered_intervals as (
    select
        rail_id,
        service,
        payer,
        payee,
        token,
        operator,
        validator,
        is_arr_eligible,
        block_number as start_block,
        log_index as start_log_index,
        ordinal as start_ordinal,
        lead(ordinal) over (partition by rail_id order by ordinal) as next_ordinal,
        terminated_ordinal,
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
        operator,
        validator,
        is_arr_eligible,
        start_block,
        start_log_index,
        start_ordinal,
        case
            when terminated_ordinal is null and next_ordinal is null then null
            when terminated_ordinal is null then next_ordinal
            when next_ordinal is null then terminated_ordinal
            when next_ordinal <= terminated_ordinal then next_ordinal
            else terminated_ordinal
        end as end_ordinal,
        rate_wei_per_epoch
    from ordered_intervals
)
select
    rail_id,
    service,
    payer,
    payee,
    token,
    operator,
    validator,
    is_arr_eligible,
    start_block,
    start_log_index,
    start_ordinal,
    date(to_timestamp(start_block * 30 + (select genesis_timestamp from params))) as start_date,
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
        else date(to_timestamp(cast(end_ordinal / 1000000 as bigint) * 30 + (select genesis_timestamp from params)))
    end as end_date,
    rate_wei_per_epoch,
    cast(rate_wei_per_epoch as decimal(38, 0)) / cast(1000000000000000000 as decimal(38, 0)) as rate_token_per_epoch
from intervals
order by rail_id, start_ordinal
