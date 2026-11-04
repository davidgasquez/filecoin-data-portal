-- asset.description = Sparse FWSS data set storage states and piece flows.

-- asset.depends = model.foc_pieces
-- asset.depends = raw.riba_eth_logs_decoded
-- asset.depends = model.network_daily_fevm_checkpoints

-- asset.not_null = date
-- asset.not_null = data_set_id
-- asset.not_null = stored_pieces
-- asset.not_null = stored_bytes
-- asset.not_null = added_bytes
-- asset.not_null = removed_bytes
-- asset.assert = stored_pieces >= 0
-- asset.assert = stored_bytes >= 0
-- asset.assert = added_bytes >= 0
-- asset.assert = removed_bytes >= 0

with logs as (
    select contract_name, transaction_hash as tx, args
    from raw.riba_eth_logs_decoded
    where event_name = 'DataSetCreated'
      and contract_name in ('pdp_verifier', 'filecoin_warm_storage_service')
),
data_set_map as (
    -- Accept only a unique FWSS/PDP creation pair in the same transaction.
    select f.data_set_id, p.set_id
    from (
        select tx, cast(args ->> 'dataSetId' as bigint) as data_set_id
        from logs where contract_name = 'filecoin_warm_storage_service'
    ) as f
    join (
        select tx, cast(args ->> 'setId' as bigint) as set_id
        from logs where contract_name = 'pdp_verifier'
    ) as p using (tx)
    qualify count(*) over (partition by tx) = 1
),
events as (
    select data_set_id as set_id, added_ordinal as ordinal,
        1 as pieces, raw_size_bytes as bytes, raw_size_bytes as added, 0::bigint as removed
    from model.foc_pieces
    union all
    select data_set_id, removed_ordinal, -1, -raw_size_bytes, 0,
        case when removed_by = 'PiecesRemoved' then raw_size_bytes else 0 end
    from model.foc_pieces
    where removed_ordinal is not null
),
checkpoints as (
    select checkpoint_ordinal, min(date) as date
    from model.network_daily_fevm_checkpoints
    where date < current_date
    group by 1
),
dated as (
    select events.*, checkpoints.date
    from events
    asof join checkpoints on checkpoints.checkpoint_ordinal >= events.ordinal
),
daily as (
    select m.data_set_id, e.date, sum(e.pieces) as pieces, sum(e.bytes) as bytes,
        sum(e.added) as added, sum(e.removed) as removed
    from dated as e join data_set_map as m using (set_id)
    group by 1, 2
)
select date, data_set_id,
    cast(sum(pieces) over w as bigint) as stored_pieces,
    cast(sum(bytes) over w as bigint) as stored_bytes,
    cast(added as bigint) as added_bytes,
    cast(removed as bigint) as removed_bytes
from daily
window w as (partition by data_set_id order by date)
order by date desc, data_set_id
