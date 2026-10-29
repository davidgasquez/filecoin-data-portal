-- asset.description = Daily unique PieceCID bytes registered in PDP data sets and the share registered with 2+ distinct storage providers.

-- asset.depends = model.network_daily_fevm_checkpoints
-- asset.depends = model.foc_pieces
-- asset.depends = raw.riba_eth_logs_decoded

-- asset.column = date | UTC date.
-- asset.column = registered_bytes | Exact raw bytes registered in all PDP data sets at end of day, counting every piece entry including copies.
-- asset.column = unique_bytes | Exact raw bytes of unique PieceCIDs registered in any PDP data set at end of day.
-- asset.column = replicated_bytes | Exact raw bytes of unique PieceCIDs registered with 2+ distinct storage providers at end of day.
-- asset.column = replication_coverage | Replicated bytes over unique bytes. Registered inventory only, not proof freshness or physical copies.

-- asset.not_null = date
-- asset.not_null = registered_bytes
-- asset.not_null = unique_bytes
-- asset.not_null = replicated_bytes
-- asset.unique = date
-- asset.assert = unique_bytes between 0 and registered_bytes
-- asset.assert = replicated_bytes between 0 and unique_bytes
-- asset.assert = replication_coverage between 0 and 1

with days as (
    select date, checkpoint_ordinal
    from model.network_daily_fevm_checkpoints
),
-- Data set storage provider over [start_ordinal, end_ordinal), from creation and handoffs.
provider_events as (
    select
        cast(json_extract_string(args, '$.setId') as bigint) as data_set_id,
        lower(coalesce(
            json_extract_string(args, '$.storageProvider'),
            json_extract_string(args, '$.newStorageProvider')
        )) as provider,
        block_number * 1000000 + log_index as start_ordinal
    from raw.riba_eth_logs_decoded
    where contract_name = 'pdp_verifier'
      and event_name in ('DataSetCreated', 'StorageProviderChanged')
),
providers as (
    select
        *,
        lead(start_ordinal) over (partition by data_set_id order by start_ordinal) as end_ordinal
    from provider_events
),
-- Piece lifetimes split at provider handoffs.
holdings as (
    select
        pieces.piece_cid,
        pieces.raw_size_bytes,
        providers.provider,
        greatest(pieces.added_ordinal, providers.start_ordinal) as start_ordinal,
        -- least() skips nulls; null only while the piece is still held.
        least(pieces.removed_ordinal, providers.end_ordinal) as end_ordinal
    from model.foc_pieces as pieces
    join providers
        on pieces.data_set_id = providers.data_set_id
        and (providers.end_ordinal is null or providers.end_ordinal > pieces.added_ordinal)
        and (pieces.removed_ordinal is null or pieces.removed_ordinal > providers.start_ordinal)
),
deltas as (
    select piece_cid, raw_size_bytes, provider, start_ordinal as ordinal, 1 as delta from holdings
    union all
    select piece_cid, raw_size_bytes, provider, end_ordinal, -1 from holdings where end_ordinal is not null
),
-- Each event lands on the first day whose end-of-day checkpoint covers it,
-- matching other FEVM daily models; events after the latest checkpoint are excluded.
dated as (
    select days.date, deltas.piece_cid, deltas.raw_size_bytes, deltas.provider, deltas.delta
    from deltas
    asof join (
        -- Carried-forward checkpoints repeat; keep the first day for each.
        select checkpoint_ordinal, min(date) as date from days group by 1
    ) as days on days.checkpoint_ordinal >= deltas.ordinal
),
-- End-of-day entries per PieceCID and provider, on days they change.
cid_providers as (
    select
        piece_cid,
        any_value(raw_size_bytes) as raw_size_bytes,
        provider,
        date,
        sum(sum(delta)) over (partition by piece_cid, provider order by date) as entries
    from dated
    group by piece_cid, provider, date
),
-- Distinct providers per PieceCID change when a provider's entries cross zero.
cid_provider_deltas as (
    select
        piece_cid,
        raw_size_bytes,
        date,
        (entries > 0)::int - coalesce(lag(entries) over (partition by piece_cid, provider order by date) > 0, false)::int as delta
    from cid_providers
),
cids as (
    select
        piece_cid,
        raw_size_bytes,
        date,
        sum(sum(delta)) over (partition by piece_cid order by date) as providers
    from cid_provider_deltas
    group by piece_cid, raw_size_bytes, date
),
cid_deltas as (
    select
        date,
        raw_size_bytes * ((providers >= 1)::int - coalesce(lag(providers) over w >= 1, false)::int) as unique_bytes,
        raw_size_bytes * ((providers >= 2)::int - coalesce(lag(providers) over w >= 2, false)::int) as replicated_bytes
    from cids
    window w as (partition by piece_cid order by date)
),
daily_deltas as (
    select
        days.date,
        coalesce(sum(cid_deltas.unique_bytes), 0) as unique_bytes,
        coalesce(sum(cid_deltas.replicated_bytes), 0) as replicated_bytes
    from days
    left join cid_deltas using (date)
    where days.date >= (select min(date) from cid_deltas)
    group by 1
),
totals as (
    select
        date,
        cast(sum(coalesce(registered_bytes, 0)) over (order by date) as bigint) as registered_bytes,
        cast(sum(unique_bytes) over (order by date) as bigint) as unique_bytes,
        cast(sum(replicated_bytes) over (order by date) as bigint) as replicated_bytes
    from daily_deltas
    left join (
        -- Every registration counts here; provider handoffs cancel without adding copies.
        select date, sum(raw_size_bytes * delta) as registered_bytes
        from dated
        group by date
    ) as registered using (date)
)
select
    date,
    registered_bytes,
    unique_bytes,
    replicated_bytes,
    replicated_bytes / nullif(unique_bytes, 0) as replication_coverage
from totals
order by date desc
