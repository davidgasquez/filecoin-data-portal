-- asset.description = Filecoin Pay payment events.

-- asset.depends = model.pay_payments

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
    gross_amount,
    net_payee_amount,
    operator_commission,
    network_fee,
    gross_amount_usd
from model.pay_payments
order by event_at desc
