-- asset.description = Filecoin Pay payment events.

-- asset.depends = raw.fevm_eth_logs_decoded
-- asset.depends = model.filecoin_pay_rails

-- asset.column = date | UTC event date.
-- asset.column = event_at | UTC event timestamp.
-- asset.column = block_number | Event block number.
-- asset.column = transaction_hash | Event transaction hash.
-- asset.column = event_name | Payment event name.
-- asset.column = rail_id | Filecoin Pay rail identifier.
-- asset.column = payer | Payer address.
-- asset.column = payee | Payee address.
-- asset.column = operator | Operator address.
-- asset.column = service_fee_recipient | Service fee recipient address.
-- asset.column = token | ERC20 token address.
-- asset.column = token_symbol | ERC20 token symbol.
-- asset.column = token_decimals | ERC20 token decimals.
-- asset.column = is_stablecoin | Whether the rail token is a tagged stablecoin.
-- asset.column = gross_amount | Gross amount paid, in token units.
-- asset.column = net_payee_amount | Net amount credited to the payee, in token units.
-- asset.column = operator_commission | Operator commission, in token units.
-- asset.column = network_fee | Network fee, in token units.
-- asset.column = gross_amount_usd | Gross amount paid in USD for tagged stablecoins.

-- asset.not_null = date
-- asset.not_null = event_at
-- asset.not_null = block_number
-- asset.not_null = transaction_hash
-- asset.not_null = event_name
-- asset.not_null = rail_id
-- asset.not_null = payer
-- asset.not_null = payee
-- asset.not_null = operator
-- asset.not_null = token
-- asset.not_null = is_stablecoin

with payment_events as (
    select
        events.file_date as date,
        to_timestamp(events.block_number * 30 + 1598306400) as event_at,
        events.block_number,
        events.transaction_hash,
        events.event_name,
        rails.rail_id,
        rails.payer,
        rails.payee,
        rails.operator,
        rails.service_fee_recipient,
        rails.token,
        rails.token_symbol,
        rails.token_decimals,
        rails.is_stablecoin,
        case
            when events.event_name = 'RailSettled' then
                cast(json_extract_string(events.args, '$.totalSettledAmount') as decimal(38, 0))
            when events.event_name = 'RailOneTimePaymentProcessed' then
                cast(json_extract_string(events.args, '$.netPayeeAmount') as decimal(38, 0))
                + cast(json_extract_string(events.args, '$.operatorCommission') as decimal(38, 0))
                + cast(json_extract_string(events.args, '$.networkFee') as decimal(38, 0))
        end as gross_amount_base_units,
        case
            when events.event_name = 'RailSettled' then
                cast(json_extract_string(events.args, '$.totalNetPayeeAmount') as decimal(38, 0))
            when events.event_name = 'RailOneTimePaymentProcessed' then
                cast(json_extract_string(events.args, '$.netPayeeAmount') as decimal(38, 0))
        end as net_payee_amount_base_units,
        cast(json_extract_string(events.args, '$.operatorCommission') as decimal(38, 0))
            as operator_commission_base_units,
        cast(json_extract_string(events.args, '$.networkFee') as decimal(38, 0))
            as network_fee_base_units
    from raw.fevm_eth_logs_decoded as events
    join model.filecoin_pay_rails as rails
        on cast(json_extract_string(events.args, '$.railId') as bigint) = rails.rail_id
    where events.contract_name = 'filecoin_pay_v1'
      and events.event_name in ('RailSettled', 'RailOneTimePaymentProcessed')
)
select
    date,
    event_at,
    block_number,
    transaction_hash,
    event_name,
    rail_id,
    payer,
    payee,
    operator,
    service_fee_recipient,
    token,
    token_symbol,
    token_decimals,
    is_stablecoin,
    gross_amount_base_units / power(cast(10 as decimal(38, 0)), token_decimals) as gross_amount,
    net_payee_amount_base_units / power(cast(10 as decimal(38, 0)), token_decimals) as net_payee_amount,
    operator_commission_base_units / power(cast(10 as decimal(38, 0)), token_decimals) as operator_commission,
    network_fee_base_units / power(cast(10 as decimal(38, 0)), token_decimals) as network_fee,
    case
        when is_stablecoin then gross_amount_base_units / power(cast(10 as decimal(38, 0)), token_decimals)
    end as gross_amount_usd
from payment_events
order by event_at desc
