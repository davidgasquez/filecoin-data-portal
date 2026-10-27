-- asset.description = ServiceOrchestrators admitted to the Solstice Service Rewards Actor.

-- asset.depends = raw.riba_eth_logs_decoded
-- asset.depends = model.foc_orchestrator_bindings

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

-- asset.not_null = orchestrator
-- asset.not_null = wallet
-- asset.unique = orchestrator

with sra as (
    select
        event_name,
        args,
        block_number,
        log_index,
        transaction_hash,
        block_number * 1000000 + log_index as pos
    from raw.riba_eth_logs_decoded
    where contract_name = 'service_rewards_actor'
      and event_name in ('OrchestratorAdmitted', 'OrchestratorRemoved', 'OrchestratorWalletReplaced')
),
admissions as (
    select
        lower(json_extract_string(args, '$.orch')) as orchestrator,
        lower(json_extract_string(args, '$.wallet')) as wallet,
        block_number,
        log_index,
        transaction_hash,
        pos,
        count(*) over (partition by lower(json_extract_string(args, '$.orch'))) as admissions,
        min(block_number) over (partition by lower(json_extract_string(args, '$.orch'))) as first_admitted_block
    from sra
    where event_name = 'OrchestratorAdmitted'
    qualify row_number() over (
        partition by lower(json_extract_string(args, '$.orch'))
        order by pos desc
    ) = 1
),
removals as (
    select
        a.orchestrator,
        min_by(r.block_number, r.pos) as removed_block,
        min_by(r.log_index, r.pos) as removed_log_index,
        min_by(r.transaction_hash, r.pos) as removed_transaction_hash
    from admissions as a
    join sra as r
        on r.event_name = 'OrchestratorRemoved'
        and lower(json_extract_string(r.args, '$.orch')) = a.orchestrator
        and r.pos > a.pos
    group by 1
),
wallet_replacements as (
    select
        a.orchestrator,
        max_by(lower(json_extract_string(w.args, '$.newWallet')), w.pos) as wallet,
        max_by(w.block_number, w.pos) as wallet_replaced_block,
        max_by(w.transaction_hash, w.pos) as wallet_replaced_transaction_hash
    from admissions as a
    join sra as w
        on w.event_name = 'OrchestratorWalletReplaced'
        and lower(json_extract_string(w.args, '$.oldOrch')) = a.orchestrator
        and w.pos > a.pos
    group by 1
),
bindings as (
    select
        orchestrator,
        count(*) filter (where effective_to_block is null) as bound_pairs
    from model.foc_orchestrator_bindings
    group by 1
)
select
    a.orchestrator,
    coalesce(w.wallet, a.wallet) as wallet,
    r.removed_block is null as is_admitted,
    a.admissions,
    a.first_admitted_block,
    to_timestamp(a.first_admitted_block * 30 + 1598306400) as first_admitted_at,
    a.block_number as admitted_block,
    a.log_index as admitted_log_index,
    a.transaction_hash as admitted_transaction_hash,
    to_timestamp(a.block_number * 30 + 1598306400) as admitted_at,
    r.removed_block,
    r.removed_log_index,
    r.removed_transaction_hash,
    to_timestamp(r.removed_block * 30 + 1598306400) as removed_at,
    w.wallet_replaced_block,
    w.wallet_replaced_transaction_hash,
    coalesce(b.bound_pairs, 0) as bound_pairs
from admissions as a
left join removals as r using (orchestrator)
left join wallet_replacements as w using (orchestrator)
left join bindings as b using (orchestrator)
order by a.block_number desc, a.log_index desc
