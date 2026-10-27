-- asset.description = Daily warm storage data stored in PDP data sets, counting every stored copy.

-- asset.depends = model.network_daily_fevm_checkpoints
-- asset.depends = model.foc_pieces
-- asset.depends = model.foc_data_sets

-- asset.column = date | UTC date.
-- asset.column = stored_pieces | Pieces added and not yet removed at end of day.
-- asset.column = stored_bytes | Exact raw PieceCIDv2 payload bytes of stored pieces at end of day.

-- asset.not_null = date
-- asset.not_null = stored_pieces
-- asset.not_null = stored_bytes
-- asset.unique = date
-- asset.assert = stored_pieces >= 0
-- asset.assert = stored_bytes >= 0

with days as (
    select date, checkpoint_ordinal
    from model.network_daily_fevm_checkpoints
),
pieces as (
    select pieces.*
    from model.foc_pieces as pieces
    join model.foc_data_sets as datasets
        on pieces.data_set_id = datasets.data_set_id
),
deltas as (
    select added_ordinal as ordinal, 1 as pieces, raw_size_bytes as bytes from pieces
    union all
    select removed_ordinal, -1, -raw_size_bytes from pieces where removed_ordinal is not null
),
-- Each event lands on the first day whose end-of-day checkpoint covers it,
-- matching other FEVM daily models; events after the latest checkpoint are excluded.
dated as (
    select days.date, deltas.pieces, deltas.bytes
    from deltas
    asof join (
        -- Carried-forward checkpoints repeat; keep the first day for each.
        select checkpoint_ordinal, min(date) as date from days group by 1
    ) as days on days.checkpoint_ordinal >= deltas.ordinal
),
daily_deltas as (
    select
        days.date,
        coalesce(sum(dated.pieces), 0) as pieces,
        coalesce(sum(dated.bytes), 0) as bytes
    from days
    left join dated using (date)
    where days.date >= (select min(date) from dated)
    group by 1
)
select
    date,
    cast(sum(pieces) over (order by date) as bigint) as stored_pieces,
    cast(sum(bytes) over (order by date) as bigint) as stored_bytes
from daily_deltas
order by date desc
