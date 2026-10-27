-- asset.description = Recomputed quarterly Filecoin Pay Volume (FIP-0118 FPV) per ServiceOrchestrator, in exact atto-USD.

-- asset.depends = raw.riba_eth_logs
-- asset.depends = raw.riba_eth_logs_decoded
-- asset.depends = raw.solstice_deployments
-- asset.depends = raw.contracts_registry
-- asset.depends = model.foc_orchestrator_bindings
-- asset.depends = model.foc_orchestrator_quarterly_fil_volumes
-- asset.depends = model.foc_orchestrator_settlements
-- asset.depends = model.foc_service_orchestrators
-- asset.depends = model.pay_rails

-- asset.column = quarter | Solstice quarter number (1 = activation quarter).
-- asset.column = orchestrator | ServiceOrchestrator identity address.
-- asset.column = start_block | First epoch of the quarter.
-- asset.column = end_block | Last epoch of the quarter.
-- asset.column = as_of_block | Last epoch covered by contiguous decoded source logs (capped at UTC yesterday).
-- asset.column = is_complete | Whether source coverage reaches the quarter end.
-- asset.column = stablecoin_settlements | Attributed admitted-stablecoin settlement events; NULL when source or binding coverage is unknown.
-- asset.column = stablecoin_volume_atto_usd | Attributed admitted-stablecoin gross settled amount, in atto-USD; NULL if unknown.
-- asset.column = fil_volume_atto_usd | Attributed FIL priced by the quarter's fee-auction prints, in atto-USD; NULL if unknown.
-- asset.column = fil_pending_atto_fil | Attributed FIL settled by the quarter end (or coverage) and not priced yet (rolls forward), in attoFIL; NULL if unknown.
-- asset.column = volume_atto_usd | FPV in atto-USD (stablecoin plus FIL); NULL if any part is unknown.
-- asset.column = is_removed_in_quarter | Whether the orchestrator was removed during the quarter (excluded from the aggregate).

-- asset.not_null = quarter
-- asset.not_null = orchestrator
-- asset.assert = volume_atto_usd is null or volume_atto_usd = stablecoin_volume_atto_usd + fil_volume_atto_usd

with params as (
    select activation_epoch as a, epochs_per_quarter as l, 1598306400 as genesis_timestamp
    from raw.solstice_deployments
    where chain_id = 314
),
covered_days as (
    -- Raw partitions decoded at the same ETag, contiguous from the first one, up to UTC yesterday.
    select file_date
    from (select distinct file_date, source_etag from raw.riba_eth_logs) as raw_dates
    left join (select distinct file_date, source_etag, true as is_decoded from raw.riba_eth_logs_decoded)
        using (file_date, source_etag)
    where file_date < timezone('UTC', now())::date
    qualify bool_and(is_decoded is not null) over (order by file_date)
        and count(*) over (order by file_date) = file_date - min(file_date) over () + 1
),
coverage as (
    -- Last epoch of the last covered UTC day.
    select
        ((max(d.file_date) + 1 - date '1970-01-01') * 86400 - p.genesis_timestamp) // 30 - 1 as as_of_block,
        -- Later bindings can back-cover earlier payments; do not mix them with a truncated prefix.
        (select max(file_date) from raw.riba_eth_logs) is distinct from max(d.file_date) as has_unverified_days
    from covered_days as d
    cross join params as p
    group by p.genesis_timestamp
),
quarters as (
    select
        q as quarter,
        p.a + (q - 1) * p.l as start_block,
        p.a + q * p.l - 1 as end_block,
        least(p.a + q * p.l - 1, c.as_of_block) as as_of_block,
        c.as_of_block >= p.a + q * p.l - 1 as is_complete,
        c.has_unverified_days
    from params as p
    cross join coverage as c
    cross join range(1, (c.as_of_block - p.a) // p.l + 2) as r(q)
    where c.as_of_block >= p.a
),
admitted_lists as (
    -- Full snapshots apply from the next quarter; the latest one before Start(Q) governs Q.
    select
        q.quarter,
        arg_max(s.args, (s.block_number, s.log_index)) as lists
    from quarters as q
    join raw.riba_eth_logs_decoded as s
        on s.contract_name = 'service_rewards_actor'
        and s.event_name = 'AdmittedListsUpdated'
        and s.block_number < q.start_block
    group by q.quarter
),
admitted as (
    select quarter, lower(unnest(json_extract_string(lists, '$.filecoinPayContracts[*]'))) as contract, null as token
    from admitted_lists
    -- Admission lists are sets; repeated addresses must not multiply payments.
    union
    select quarter, null, lower(unnest(json_extract_string(lists, '$.stablecoins[*]')))
    from admitted_lists
),
unknown_contracts as (
    select distinct a.quarter
    from admitted as a
    where a.contract is not null
      and not exists (
          select 1 from raw.contracts_registry as r
          where lower(r.address) = a.contract and r.contract_name = 'filecoin_pay_v1'
      )
),
attributed as (
    select * from model.foc_orchestrator_settlements where orchestrator is not null
),
decimals as (
    select token, any_value(token_decimals) as token_decimals
    from model.pay_rails
    where token_decimals is not null
    group by token
),
stablecoin as (
    select
        q.quarter,
        a.orchestrator,
        count(*) as settlements,
        -- Exact integer scale to 18 decimals; unknown or >18 decimals is unknown, not guessed.
        sum(a.amount * cast('1' || repeat('0', 18 - d.token_decimals) as hugeint)) as volume,
        bool_or(d.token_decimals is null or d.token_decimals > 18) as is_unknown
    from attributed as a
    join quarters as q
        on a.block_number between q.start_block and q.as_of_block
    join admitted as c on c.quarter = q.quarter and c.contract = a.contract
    join admitted as t on t.quarter = q.quarter and t.token = a.token
    left join decimals as d on d.token = a.token and d.token_decimals <= 18
    group by q.quarter, a.orchestrator
),
fil as (
    -- Renamed so select aliases below are not shadowed by joined columns.
    select quarter, orchestrator, fil_volume_atto_usd as usd, fil_pending_atto_fil as pending
    from model.foc_orchestrator_quarterly_fil_volumes
),
unknown_quarters as (
    -- A span with unknown start may back-cover from its event quarter's start.
    select distinct q.quarter, b.orchestrator
    from model.foc_orchestrator_bindings as b
    cross join params as p
    join quarters as q
        on p.a + (greatest(if(b.start_block < p.a, 0, (b.start_block - p.a) // p.l + 1), 1) - 1) * p.l <= q.as_of_block
        and (b.effective_to_block is null or b.effective_to_block >= q.start_block)
    where b.effective_from_block is null
),
removals as (
    select lower(json_extract_string(args, '$.orch')) as orchestrator, block_number
    from raw.riba_eth_logs_decoded
    where contract_name = 'service_rewards_actor'
      and event_name = 'OrchestratorRemoved'
)
select
    q.quarter,
    o.orchestrator,
    q.start_block,
    q.end_block,
    q.as_of_block,
    q.is_complete,
    case
        when (q.has_unverified_days and not q.is_complete) or l.quarter is null or u.quarter is not null or c.quarter is not null then null
        else coalesce(s.settlements, 0)
    end as stablecoin_settlements,
    case
        when (q.has_unverified_days and not q.is_complete) or l.quarter is null or u.quarter is not null or c.quarter is not null or s.is_unknown then null
        else coalesce(s.volume, 0)
    end as stablecoin_volume_atto_usd,
    case
        when (q.has_unverified_days and not q.is_complete) or l.quarter is null or u.quarter is not null or c.quarter is not null then null
        -- No row: the orchestrator has no attributed FIL settlement.
        when f.quarter is null then 0::hugeint
        else f.usd::hugeint
    end as fil_volume_atto_usd,
    case
        when (q.has_unverified_days and not q.is_complete) or l.quarter is null or u.quarter is not null or c.quarter is not null then null
        when f.quarter is null then 0::hugeint
        else f.pending::hugeint
    end as fil_pending_atto_fil,
    stablecoin_volume_atto_usd + fil_volume_atto_usd as volume_atto_usd,
    exists (
        select 1 from removals as r
        where r.orchestrator = o.orchestrator
          and r.block_number between q.start_block and q.end_block
    ) as is_removed_in_quarter
from quarters as q
join model.foc_service_orchestrators as o
    on o.first_admitted_block <= q.end_block
left join admitted_lists as l on l.quarter = q.quarter
left join unknown_contracts as c on c.quarter = q.quarter
left join unknown_quarters as u on u.quarter = q.quarter and u.orchestrator = o.orchestrator
left join stablecoin as s on s.quarter = q.quarter and s.orchestrator = o.orchestrator
left join fil as f on f.quarter = q.quarter and f.orchestrator = o.orchestrator
order by q.quarter desc, o.orchestrator
