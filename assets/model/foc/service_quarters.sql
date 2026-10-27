-- asset.description = Solstice quarters with their on-chain bound FPV aggregate, share submission, and SWA gate check.

-- asset.depends = raw.riba_eth_logs
-- asset.depends = raw.riba_eth_logs_decoded
-- asset.depends = raw.solstice_deployments

-- asset.column = quarter | Solstice quarter number (1 = activation quarter).
-- asset.column = start_block | First epoch of the quarter.
-- asset.column = end_block | Last epoch of the quarter.
-- asset.column = posting_start_block | First epoch of the posting window (the next quarter start).
-- asset.column = verification_start_block | First epoch of the verification (correction) window.
-- asset.column = bound_block | First epoch when posted volumes are bound.
-- asset.column = as_of_block | Last epoch covered by contiguous decoded source logs (capped at UTC yesterday).
-- asset.column = is_bound | Whether source coverage reaches the bound epoch.
-- asset.column = bound_volume_atto_usd | SRA aggregated FPV (posts and corrections, removals never deducted), in atto-USD; NULL until bound.
-- asset.column = shares_submitted_at | Observed SharesSubmitted timestamp; all-zero submissions emit no event.
-- asset.column = share_recipients | Recipients in the observed submitted share map.
-- asset.column = shares_total_atto_usd | USD total over admitted recipients in the observed share map.
-- asset.column = gate_checked_at | Observed SWA gate check timestamp; quarter 1 is never gated.
-- asset.column = gate_passed | Whether the bound FPV met the gate threshold; NULL if not checked.
-- asset.column = gate_steps | Gate steps after the check.
-- asset.column = gate_threshold_atto_usd | Threshold applied (base * stepRatio^steps, FixedU18 floor math), in atto-USD; NULL if arithmetic exceeds HUGEINT.

-- asset.not_null = quarter
-- asset.unique = quarter
-- asset.assert = gate_checked_at is null or quarter >= 2
-- asset.assert = gate_passed is null or bound_volume_atto_usd is null or gate_passed = (bound_volume_atto_usd >= gate_threshold_atto_usd)

with recursive params as (
    select activation_epoch as a, epochs_per_quarter as l, post_period as p, verification_window as v
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
    select ((max(file_date) + 1 - date '1970-01-01') * 86400 - 1598306400) // 30 - 1 as as_of_block
    from covered_days
),
quarters as (
    select
        q as quarter,
        p.a + (q - 1) * p.l as start_block,
        p.a + q * p.l - 1 as end_block,
        p.a + q * p.l as posting_start_block,
        p.a + q * p.l + p.p as verification_start_block,
        p.a + q * p.l + p.p + p.v as bound_block,
        c.as_of_block,
        -- SRA _afterBinding: now >= verifyEnd.
        c.as_of_block >= p.a + q * p.l + p.p + p.v as is_bound
    from params as p
    cross join coverage as c
    cross join range(1, (c.as_of_block - p.a) // p.l + 2) as r(q)
    where c.as_of_block >= p.a
),
events as (
    select
        event_name,
        args,
        block_number * 1000000 + log_index as pos,
        to_timestamp(1598306400 + block_number * 30) as event_at
    from raw.riba_eth_logs_decoded
    where block_number <= (select as_of_block from coverage)
      and (
        (contract_name = 'service_rewards_actor' and event_name in ('VolumePosted', 'VolumeCorrected', 'SharesSubmitted'))
        or (contract_name = 'stream_weight_actor' and event_name in ('GateParamsSet', 'QuarterlyGateCheckResult'))
      )
),
volumes as (
    -- totalUsd[q] += value - previous value, so it sums each orchestrator's latest write (0 clears).
    -- Removal and readmission only happen after q binds, so the address keys one identity per quarter.
    select quarter, sum(volume) as volume
    from (
        select
            json_extract_string(args, '$.q')::bigint as quarter,
            arg_max(json_extract_string(args, '$.volume')::hugeint, pos) as volume
        from events
        where event_name in ('VolumePosted', 'VolumeCorrected')
        group by quarter, lower(json_extract_string(args, '$.orchestrator'))
    )
    group by quarter
),
shares as (
    select
        json_extract_string(args, '$.q')::bigint as quarter,
        event_at as shares_submitted_at,
        json_extract_string(args, '$.recipientCount')::bigint as share_recipients,
        json_extract_string(args, '$.totalUsd')::hugeint as shares_total_atto_usd
    from events
    where event_name = 'SharesSubmitted'
),
gate_params as (
    select
        pos,
        try_cast(json_extract_string(args, '$.params.target.base') as hugeint) as base,
        try_cast(json_extract_string(args, '$.params.target.stepRatio') as hugeint) as ratio
    from events
    where event_name = 'GateParamsSet'
),
checks as (
    -- The threshold uses the latest applied params before the check and the steps before it.
    select
        json_extract_string(c.args, '$.quarter')::bigint as quarter,
        c.event_at as gate_checked_at,
        json_extract_string(c.args, '$.passed')::boolean as gate_passed,
        json_extract_string(c.args, '$.steps')::bigint as gate_steps,
        -- Initial params (GateParamsLibrary.init) until the first GateParamsSet.
        if(g.pos is null, 3500000000000000000000::hugeint, g.base) as base,
        if(g.pos is null, 2700000000000000000::hugeint, g.ratio) as ratio
    from events as c
    asof left join gate_params as g on c.pos > g.pos
    where c.event_name = 'QuarterlyGateCheckResult'
),
power as (
    -- FixedU18.exp square-and-multiply; x*y//1e18 is split to stay exact within HUGEINT.
    select quarter, ratio as b, 1000000000000000000::hugeint as p, gate_steps - gate_passed::int as e
    from checks
    union all
    select
        quarter,
        try(
            (b // 1000000000000000000) * b + (b % 1000000000000000000) * (b // 1000000000000000000)
                + (b % 1000000000000000000) * (b % 1000000000000000000) // 1000000000000000000
        ),
        if(
            e % 2 = 1,
            try((b // 1000000000000000000) * p + (b % 1000000000000000000) * (p // 1000000000000000000)
                + (b % 1000000000000000000) * (p % 1000000000000000000) // 1000000000000000000),
            p
        ),
        e // 2
    from power
    where e > 1
),
thresholds as (
    select
        c.quarter,
        if(w.e = 0, w.p,
            try((w.b // 1000000000000000000) * w.p + (w.b % 1000000000000000000) * (w.p // 1000000000000000000)
                + (w.b % 1000000000000000000) * (w.p % 1000000000000000000) // 1000000000000000000)
        ) as x,
        c.base
    from checks as c
    join power as w on w.quarter = c.quarter and w.e <= 1
)
select
    q.quarter,
    q.start_block,
    q.end_block,
    q.posting_start_block,
    q.verification_start_block,
    q.bound_block,
    q.as_of_block,
    q.is_bound,
    if(q.is_bound, coalesce(v.volume, 0::hugeint), null) as bound_volume_atto_usd,
    s.shares_submitted_at,
    s.share_recipients,
    s.shares_total_atto_usd,
    c.gate_checked_at,
    c.gate_passed,
    c.gate_steps,
    try((t.base // 1000000000000000000) * t.x + (t.base % 1000000000000000000) * (t.x // 1000000000000000000)
        + (t.base % 1000000000000000000) * (t.x % 1000000000000000000) // 1000000000000000000)
        as gate_threshold_atto_usd
from quarters as q
left join volumes as v on v.quarter = q.quarter
left join shares as s on s.quarter = q.quarter
left join checks as c on c.quarter = q.quarter
left join thresholds as t on t.quarter = q.quarter
order by q.quarter desc
