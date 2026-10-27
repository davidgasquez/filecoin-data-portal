-- asset.description = Effective (payer, operator) attribution spans per ServiceOrchestrator, from SRA registry events.

-- asset.depends = raw.riba_eth_logs_decoded
-- asset.depends = raw.solstice_deployments

-- asset.column = payer | Rail payer address.
-- asset.column = operator | Rail operator address.
-- asset.column = orchestrator | ServiceOrchestrator identity address credited in the span.
-- asset.column = effective_from_block | Inclusive span start block, after back-cover, cutoff, and inherit; NULL if the cutoff is unknown.
-- asset.column = effective_from_log_index | Inclusive span start log index within the block.
-- asset.column = effective_to_block | Exclusive span end block (release or replacement event); NULL while open.
-- asset.column = effective_to_log_index | Exclusive span end log index; NULL while open.
-- asset.column = effective_from_quarter | Solstice quarter containing the span start.
-- asset.column = effective_from_at | UTC span start timestamp.
-- asset.column = effective_to_at | UTC span end timestamp, if closed.
-- asset.column = start_event | Event that started the span (BindingDeclared or BindingReassigned).
-- asset.column = start_block | Starting event block.
-- asset.column = start_log_index | Starting event log index.
-- asset.column = start_transaction_hash | Starting event transaction hash.
-- asset.column = inherit | Reassignment inherit flag, if the span started with a reassignment.
-- asset.column = end_event | Event that ended the span (BindingReassigned, BindingCanceled, OrchestratorRemoved), if any.
-- asset.column = end_block | Ending event block, if any.
-- asset.column = end_log_index | Ending event log index, if any.
-- asset.column = end_transaction_hash | Ending event transaction hash, if any.

-- asset.not_null = payer
-- asset.not_null = operator
-- asset.not_null = orchestrator
-- asset.not_null = start_block
-- asset.assert = effective_to_block is null or effective_from_block is null or (effective_from_block, effective_from_log_index) < (effective_to_block, effective_to_log_index)

with recursive params as (
    -- Positions below encode (block, log_index) as block * 1e6 + log_index.
    select
        activation_epoch as a,
        epochs_per_quarter as l,
        1598306400 as genesis_timestamp
    from raw.solstice_deployments
    where chain_id = 314
),
sra as (
    select
        event_name,
        args,
        block_number,
        log_index,
        transaction_hash,
        block_number * 1000000 + log_index as pos,
        if(block_number < p.a, 0, (block_number - p.a) // p.l + 1) as q
    from raw.riba_eth_logs_decoded
    cross join params as p
    where contract_name = 'service_rewards_actor'
),
pair_events as (
    select
        lower(json_extract_string(args, '$.payer')) as payer,
        lower(json_extract_string(args, '$.operator')) as operator,
        lower(json_extract_string(args, '$.orchestrator')) as orch,
        event_name,
        cast(json_extract_string(args, '$.inherit') as boolean) as inherit,
        block_number, log_index, transaction_hash, pos, q
    from sra
    where event_name in ('BindingDeclared', 'BindingReassigned', 'BindingCanceled')
),
removals as (
    -- Removal releases every pair the orchestrator holds; the walk checks the holder.
    select pairs.payer, pairs.operator, pairs.orch, sra.event_name, null::boolean,
        sra.block_number, sra.log_index, sra.transaction_hash, sra.pos, sra.q
    from sra
    join (select distinct payer, operator, orch from pair_events) as pairs
        on pairs.orch = lower(json_extract_string(sra.args, '$.orch'))
    where sra.event_name = 'OrchestratorRemoved'
),
events as (
    select
        e.*,
        -- Quarter 0 registrations apply from activation, as in the reference indexer.
        (p.a + (greatest(e.q, 1) - 1) * p.l) * 1000000 as q_start_pos,
        (p.a + e.q * p.l) * 1000000 as next_q_start_pos,
        (
            select cast(json_extract_string(c.args, '$.registrationCutoff') as bigint)
            from sra as c
            where c.event_name = 'PricingParamsUpdated'
              and c.block_number < p.a + (greatest(e.q, 1) - 1) * p.l
            order by c.pos desc
            limit 1
        ) as cutoff,
        e.event_name in ('BindingCanceled', 'OrchestratorRemoved') as is_release,
        row_number() over (partition by e.payer, e.operator order by e.pos) as n
    from (select * from pair_events union all select * from removals) as e
    cross join params as p
),
walk as (
    select
        payer, operator, 0::bigint as n,
        null::varchar as holder, null::bigint as from_pos, null::bigint as release_pos,
        null::varchar as start_event, null::bigint as start_block, null::bigint as start_log_index,
        null::varchar as start_transaction_hash, null::boolean as inherit,
        false as closes, null::varchar as prev_holder, null::bigint as prev_from_pos,
        null::varchar as prev_start_event, null::bigint as prev_start_block,
        null::bigint as prev_start_log_index, null::varchar as prev_start_transaction_hash,
        null::boolean as prev_inherit,
        null::varchar as end_event, null::bigint as end_block, null::bigint as end_log_index,
        null::varchar as end_transaction_hash, null::bigint as end_pos
    from (select distinct payer, operator from events)
    union all
    select
        w.payer, w.operator, e.n,
        if(x.releases, null, if(e.is_release, w.holder, e.orch)) as holder,
        case
            when x.releases then null
            when e.is_release then w.from_pos
            when x.inherits then w.from_pos
            when x.inherits is null then null
            when e.event_name = 'BindingReassigned' then e.pos
            when e.q >= 1 and e.cutoff is null then null
            when e.q >= 1 and e.block_number * 1000000 >= e.next_q_start_pos - e.cutoff * 1000000
                then e.next_q_start_pos
            else greatest(e.q_start_pos, coalesce(w.release_pos, 0))
        end as from_pos,
        if(x.releases, e.pos, w.release_pos) as release_pos,
        if(e.is_release, if(x.releases, null, w.start_event), e.event_name),
        if(e.is_release, if(x.releases, null, w.start_block), e.block_number),
        if(e.is_release, if(x.releases, null, w.start_log_index), e.log_index),
        if(e.is_release, if(x.releases, null, w.start_transaction_hash), e.transaction_hash),
        if(e.is_release, if(x.releases, null, w.inherit), e.inherit),
        w.holder is not null and (x.releases or (not e.is_release and not x.inherits)) as closes,
        w.holder, w.from_pos, w.start_event, w.start_block, w.start_log_index,
        w.start_transaction_hash, w.inherit,
        e.event_name, e.block_number, e.log_index, e.transaction_hash, e.pos
    from walk as w
    join events as e
        on e.payer = w.payer and e.operator = w.operator and e.n = w.n + 1
    cross join lateral (
        select
            e.is_release and w.holder = e.orch as releases,
            -- An unknown displaced start cannot become a known inherited start.
            e.event_name = 'BindingReassigned' and e.inherit
                and w.holder is not null and w.from_pos >= e.q_start_pos as inherits
    ) as x
),
spans as (
    select
        payer, operator, prev_holder as orchestrator, prev_from_pos as from_pos, end_pos as to_pos,
        prev_start_event as start_event, prev_start_block as start_block,
        prev_start_log_index as start_log_index, prev_start_transaction_hash as start_transaction_hash,
        prev_inherit as inherit, end_event, end_block, end_log_index, end_transaction_hash
    from walk
    where closes
    union all
    select
        payer, operator, holder, from_pos, null,
        start_event, start_block, start_log_index, start_transaction_hash, inherit,
        null, null, null, null
    from (select *, n = max(n) over (partition by payer, operator) as is_last from walk)
    where is_last and holder is not null
)
select
    s.payer,
    s.operator,
    s.orchestrator,
    s.from_pos // 1000000 as effective_from_block,
    s.from_pos % 1000000 as effective_from_log_index,
    s.to_pos // 1000000 as effective_to_block,
    s.to_pos % 1000000 as effective_to_log_index,
    if(s.from_pos // 1000000 < p.a, 0, (s.from_pos // 1000000 - p.a) // p.l + 1) as effective_from_quarter,
    to_timestamp((s.from_pos // 1000000) * 30 + p.genesis_timestamp) as effective_from_at,
    to_timestamp((s.to_pos // 1000000) * 30 + p.genesis_timestamp) as effective_to_at,
    s.start_event,
    s.start_block,
    s.start_log_index,
    s.start_transaction_hash,
    s.inherit,
    s.end_event,
    s.end_block,
    s.end_log_index,
    s.end_transaction_hash
from spans as s
cross join params as p
-- Drop spans that never applied, like a cutoff registration released before it starts.
where s.to_pos is null or s.from_pos is null or s.from_pos < s.to_pos
order by s.start_block desc, s.start_log_index desc
