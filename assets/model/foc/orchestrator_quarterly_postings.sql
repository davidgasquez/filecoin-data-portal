-- asset.description = Orchestrator FPV posts, governance corrections, and bound volume per Solstice quarter, in exact atto-USD.

-- asset.depends = raw.riba_eth_logs_decoded
-- asset.depends = model.foc_service_quarters
-- asset.depends = model.foc_orchestrator_quarterly_volumes

-- asset.column = quarter | Solstice quarter number the volume reports.
-- asset.column = orchestrator | ServiceOrchestrator identity address.
-- asset.column = as_of_block | Last epoch covered by contiguous decoded source logs (capped at UTC yesterday).
-- asset.column = is_bound | Whether source coverage reaches the quarter's bound epoch.
-- asset.column = posted_at | VolumePosted timestamp; NULL if never posted.
-- asset.column = posted_volume_atto_usd | Initial posted volume, in atto-USD; NULL if never posted.
-- asset.column = corrections | VolumeCorrected events.
-- asset.column = corrected_at | Latest VolumeCorrected timestamp.
-- asset.column = reported_volume_atto_usd | Latest written volume (post or correction; 0 clears), in atto-USD; NULL if never written.
-- asset.column = bound_volume_atto_usd | Volume counted in the SRA bound aggregate, in atto-USD; 0 if bound without writes, NULL until bound.

-- asset.not_null = quarter
-- asset.not_null = orchestrator
-- asset.not_null = is_bound
-- asset.assert = corrections > 0 or reported_volume_atto_usd is not distinct from posted_volume_atto_usd
-- asset.assert = is_bound = (bound_volume_atto_usd is not null)

with writes as (
    -- Removal (and readmission under a fresh id) is only allowed after the quarter binds, so the
    -- address keys one identity per quarter. Volumes are capped on-chain at 1e30, within HUGEINT.
    select
        e.quarter,
        lower(json_extract_string(e.args, '$.orchestrator')) as orchestrator,
        min(to_timestamp(1598306400 + e.block_number * 30)) filter (where e.event_name = 'VolumePosted') as posted_at,
        any_value(json_extract_string(e.args, '$.volume')::hugeint) filter (where e.event_name = 'VolumePosted')
            as posted_volume_atto_usd,
        count(*) filter (where e.event_name = 'VolumeCorrected') as corrections,
        max(to_timestamp(1598306400 + e.block_number * 30)) filter (where e.event_name = 'VolumeCorrected') as corrected_at,
        arg_max(json_extract_string(e.args, '$.volume')::hugeint, (e.block_number, e.log_index))
            as reported_volume_atto_usd
    from (
        select *, json_extract_string(args, '$.q')::bigint as quarter
        from raw.riba_eth_logs_decoded
        where contract_name = 'service_rewards_actor'
          and event_name in ('VolumePosted', 'VolumeCorrected')
    ) as e
    -- Same archive coverage as the quarter (no events past the first gap or UTC yesterday).
    join model.foc_service_quarters as q
        on q.quarter = e.quarter
        and e.block_number <= q.as_of_block
    group by all
),
grid as (
    -- Recomputed-FPV rows plus any writer admitted after the quarter ended.
    select quarter, orchestrator from model.foc_orchestrator_quarterly_volumes
    union
    select quarter, orchestrator from writes
)
select
    g.quarter,
    g.orchestrator,
    q.as_of_block,
    q.is_bound,
    w.posted_at,
    w.posted_volume_atto_usd,
    coalesce(w.corrections, 0) as corrections,
    w.corrected_at,
    w.reported_volume_atto_usd,
    if(q.is_bound, coalesce(w.reported_volume_atto_usd, 0::hugeint), null) as bound_volume_atto_usd
from grid as g
join model.foc_service_quarters as q on q.quarter = g.quarter
left join writes as w on w.quarter = g.quarter and w.orchestrator = g.orchestrator
order by g.quarter desc, g.orchestrator
