-- asset.description = Solstice ServiceOrchestrators.

-- asset.depends = model.foc_service_orchestrators

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

select * from model.foc_service_orchestrators
