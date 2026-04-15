-- asset.description = Published Filecoin Pay rails.

-- asset.depends = model.filecoin_pay_rails

-- asset.column = rail_id | Filecoin Pay rail identifier.
-- asset.column = payer | Payer address.
-- asset.column = payee | Payee address.
-- asset.column = token | ERC20 token address.
-- asset.column = operator | Operator address.
-- asset.column = service | Service classification.
-- asset.column = validator | Validator address.
-- asset.column = service_fee_recipient | Service fee recipient address.
-- asset.column = commission_rate_bps | Commission rate in basis points.
-- asset.column = is_arr_eligible | Whether the rail counts toward ARR.
-- asset.column = created_block | Creation block number.
-- asset.column = created_log_index | Creation log index.
-- asset.column = created_transaction_hash | Creation transaction hash.
-- asset.column = created_date | UTC creation date.
-- asset.column = terminated_block | Termination block number, if any.
-- asset.column = terminated_log_index | Termination log index, if any.
-- asset.column = terminated_transaction_hash | Termination transaction hash, if any.
-- asset.column = terminated_by | Address that terminated the rail, if any.
-- asset.column = terminated_end_epoch | End epoch emitted on termination, if any.
-- asset.column = terminated_date | UTC termination date, if any.
-- asset.column = terminated_end_date | UTC termination end date, if any.
-- asset.column = is_terminated | Whether the rail has a termination event.

select
    rail_id,
    payer,
    payee,
    token,
    operator,
    service,
    validator,
    service_fee_recipient,
    commission_rate_bps,
    is_arr_eligible,
    created_block,
    created_log_index,
    created_transaction_hash,
    created_date,
    terminated_block,
    terminated_log_index,
    terminated_transaction_hash,
    terminated_by,
    terminated_end_epoch,
    terminated_date,
    terminated_end_date,
    is_terminated
from model.filecoin_pay_rails
