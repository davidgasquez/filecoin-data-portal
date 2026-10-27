-- asset.description = Filecoin Pay rails.

-- asset.depends = model.pay_rails

-- asset.column = rail_id | Filecoin Pay rail identifier.
-- asset.column = payer | Payer address.
-- asset.column = payee | Payee address.
-- asset.column = token | ERC20 token address.
-- asset.column = token_symbol | ERC20 token symbol.
-- asset.column = token_decimals | ERC20 token decimals.
-- asset.column = is_stablecoin | Whether the rail token is a tagged stablecoin.
-- asset.column = operator | Operator address.
-- asset.column = service | Service classification.
-- asset.column = validator | Validator address.
-- asset.column = service_fee_recipient | Service fee recipient address.
-- asset.column = commission_rate_bps | Commission rate in basis points.
-- asset.column = is_arr_eligible | Whether the rail counts toward recurring run-rate (tagged stablecoin, non-Dealbot payer).
-- asset.column = created_block | Creation block number.
-- asset.column = created_log_index | Creation log index.
-- asset.column = created_transaction_hash | Creation transaction hash.
-- asset.column = created_at | UTC creation timestamp.
-- asset.column = terminated_block | Termination block number, if any.
-- asset.column = terminated_log_index | Termination log index, if any.
-- asset.column = terminated_transaction_hash | Termination transaction hash, if any.
-- asset.column = terminated_by | Address that terminated the rail, if any.
-- asset.column = terminated_end_epoch | End epoch emitted on termination, if any.
-- asset.column = terminated_at | UTC termination timestamp, if any.
-- asset.column = terminated_end_at | UTC termination end timestamp, if any.
-- asset.column = is_terminated | Whether the rail has a termination event.
-- asset.column = data_set_id | Warm Storage data set paid by the rail, if any.
-- asset.column = state | Current lifecycle state (active, terminated, finalized), from the Filecoin API.
-- asset.column = payment_rate | Current payment rate in token base units per epoch, from the Filecoin API.
-- asset.column = lockup_period | Current lockup period in epochs, from the Filecoin API.
-- asset.column = lockup_fixed | Current fixed lockup in token base units, from the Filecoin API.
-- asset.column = settled_up_to | Epoch settled up to, from the Filecoin API.
-- asset.column = total_settled_amount | Cumulative settled amount in token base units, from the Filecoin API.
-- asset.column = total_net_payee_amount | Cumulative settled amount net to payee in token base units, from the Filecoin API.
-- asset.column = total_one_time_amount | Cumulative one-time payments in token base units, from the Filecoin API.
-- asset.column = total_one_time_net_payee_amount | Cumulative one-time payments net to payee in token base units, from the Filecoin API.
-- asset.column = api_indexed_block | Latest API indexer block before the snapshot.
-- asset.column = api_observed_at | UTC Filecoin API snapshot timestamp.

select
    rail_id,
    payer,
    payee,
    token,
    token_symbol,
    token_decimals,
    is_stablecoin,
    operator,
    service,
    validator,
    service_fee_recipient,
    commission_rate_bps,
    is_arr_eligible,
    created_block,
    created_log_index,
    created_transaction_hash,
    created_at,
    terminated_block,
    terminated_log_index,
    terminated_transaction_hash,
    terminated_by,
    terminated_end_epoch,
    terminated_at,
    terminated_end_at,
    is_terminated,
    data_set_id,
    state,
    payment_rate,
    lockup_period,
    lockup_fixed,
    settled_up_to,
    total_settled_amount,
    total_net_payee_amount,
    total_one_time_amount,
    total_one_time_net_payee_amount,
    api_indexed_block,
    api_observed_at
from model.pay_rails
