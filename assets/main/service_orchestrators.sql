-- asset.description = Solstice ServiceOrchestrators.

-- asset.depends = model.foc_service_orchestrators
-- asset.depends = model.foc_daily_orchestrator_payments

-- asset.column = orchestrator | ServiceOrchestrator identity address (not the payout wallet).
-- asset.column = wallet | Current payout wallet.
-- asset.column = is_admitted | Whether the latest admission has no later removal.
-- asset.column = admissions | Number of admission events.
-- asset.column = first_admitted_block | First admission block.
-- asset.column = first_admitted_at | UTC first admission timestamp.
-- asset.column = admitted_block | Latest admission block.
-- asset.column = admitted_log_index | Latest admission log index.
-- asset.column = admitted_transaction_hash | Latest admission transaction hash.
-- asset.column = admitted_at | UTC latest admission timestamp.
-- asset.column = removed_block | Removal block after the latest admission, if any.
-- asset.column = removed_log_index | Removal log index, if any.
-- asset.column = removed_transaction_hash | Removal transaction hash, if any.
-- asset.column = removed_at | UTC removal timestamp, if any.
-- asset.column = wallet_replaced_block | Latest payout wallet replacement block since admission, if any.
-- asset.column = wallet_replaced_transaction_hash | Latest payout wallet replacement transaction hash, if any.
-- asset.column = bound_pairs | Open (payer, operator) binding spans.

-- asset.column = payment_history | Daily gross payments in token base units, ordered by date, token and payer.

select orchestrators.*, history.payment_history
from model.foc_service_orchestrators as orchestrators
left join (
    select orchestrator, list(struct_pack(
        date := date, payer := payer::varchar, token := token::varchar, amount := amount
    ) order by date, token, payer) as payment_history
    from model.foc_daily_orchestrator_payments group by orchestrator
) as history using (orchestrator)
