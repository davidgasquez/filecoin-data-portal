-- asset.description = PDP pieces with PieceCIDv2 sizes and add/removal lifecycle.

-- asset.depends = raw.riba_eth_logs_decoded

-- asset.column = data_set_id | PDP data set identifier.
-- asset.column = piece_id | Piece identifier within the data set.
-- asset.column = piece_cid | PieceCIDv2 bytes as hex.
-- asset.column = padding | Raw zero padding bytes encoded in the PieceCIDv2.
-- asset.column = height | Merkle tree height encoded in the PieceCIDv2.
-- asset.column = raw_size_bytes | Exact raw payload size, 2^(height-2) * 127 - padding.
-- asset.column = leaf_count | Data-bearing 32-byte leaves counted by the PDP verifier.
-- asset.column = added_block | Block where the piece was added.
-- asset.column = added_ordinal | Event ordinal (block * 1e6 + log index) of the addition.
-- asset.column = added_at | UTC addition timestamp.
-- asset.column = removed_block | Block where the piece was removed or its data set deleted, if any.
-- asset.column = removed_ordinal | Event ordinal of the removal or data set deletion, if any.
-- asset.column = removed_at | UTC removal timestamp, if any.
-- asset.column = removed_by | Event ending the piece (PiecesRemoved or DataSetDeleted), if any.

-- asset.not_null = data_set_id
-- asset.not_null = piece_id
-- asset.not_null = piece_cid
-- asset.not_null = padding
-- asset.not_null = height
-- asset.not_null = raw_size_bytes
-- asset.not_null = leaf_count
-- asset.assert = piece_cid like '0x01559120%'
-- asset.assert = height between 2 and 50
-- asset.assert = raw_size_bytes > 0
-- asset.assert = leaf_count > 0
-- asset.assert = leaf_count * 32 * 127 // 128 - raw_size_bytes between 0 and 31
-- asset.assert = removed_ordinal is null or removed_ordinal > added_ordinal

with logs as (
    select
        event_name,
        args,
        cast(json_extract_string(args, '$.setId') as bigint) as data_set_id,
        block_number,
        block_number * 1000000 + log_index as ordinal
    from raw.riba_eth_logs_decoded
    where contract_name = 'pdp_verifier'
      and event_name in ('PiecesAdded', 'PiecesAddedV2', 'PiecesRemoved', 'DataSetDeleted')
),
added as (
    -- Legacy event: parallel pieceIds[] and pieceCids[].data arrays (unnests zip by position).
    select
        data_set_id,
        cast(unnest(cast(args -> '$.pieceIds' as varchar[])) as bigint) as piece_id,
        substr(unnest(cast(args -> '$.pieceCids' as json[])) ->> 'data', 3) as cid,
        block_number,
        ordinal
    from logs
    where event_name = 'PiecesAdded'
    union all
    -- V2 event: ids are firstPieceId + i; header is the CID prefix right-aligned with leading zero bytes.
    select
        data_set_id,
        cast(json_extract_string(args, '$.firstPieceId') as bigint)
            + unnest(range(cast(json_array_length(args -> '$.pieceCids') as bigint))) as piece_id,
        unnest(list_transform(
            cast(args -> '$.pieceCids' as json[]),
            lambda c: regexp_extract(c ->> 'header', '^0x(?:00)*(.*)$', 1) || substr(c ->> 'root', 3)
        )) as cid,
        block_number,
        ordinal
    from logs
    where event_name = 'PiecesAddedV2'
),
parsed as (
    -- PieceCIDv2 (FRC-0069): 01 55 9120 | mh length (1 byte here) | uvarint padding | height | 32-byte root.
    select
        *,
        list_reduce(
            list_transform(
                range(cast(length(cid) // 2 - 38 as bigint)),
                lambda i: (cast('0x' || substr(cid, 11 + 2 * i, 2) as bigint) & 127) << (7 * i)
            ),
            lambda acc, x: acc + x,
            cast(0 as bigint)
        ) as padding,
        cast('0x' || substr(cid, length(cid) - 65, 2) as integer) as height
    from added
),
removals as (
    select
        data_set_id,
        cast(unnest(cast(args -> '$.pieceIds' as varchar[])) as bigint) as piece_id,
        block_number,
        ordinal,
        event_name
    from logs
    where event_name = 'PiecesRemoved'
),
deletions as (
    select data_set_id, block_number, ordinal, event_name
    from logs
    where event_name = 'DataSetDeleted'
),
pieces as (
    select
        parsed.data_set_id,
        parsed.piece_id,
        '0x' || parsed.cid as piece_cid,
        parsed.padding,
        parsed.height,
        (cast(1 as bigint) << (parsed.height - 2)) * 127 - parsed.padding as raw_size_bytes,
        (cast(1 as bigint) << parsed.height) - ((128 * parsed.padding) // 127 >> 5) as leaf_count,
        parsed.block_number as added_block,
        parsed.ordinal as added_ordinal,
        -- A piece ends at its first removal or at data set deletion, whichever comes first.
        case
            when deletions.ordinal is null or removals.ordinal < deletions.ordinal then removals.block_number
            else deletions.block_number
        end as removed_block,
        least(removals.ordinal, deletions.ordinal) as removed_ordinal,
        case
            when deletions.ordinal is null or removals.ordinal < deletions.ordinal then removals.event_name
            else deletions.event_name
        end as removed_by
    from parsed
    left join removals using (data_set_id, piece_id)
    left join deletions using (data_set_id)
)
select
    data_set_id,
    piece_id,
    piece_cid,
    padding,
    height,
    raw_size_bytes,
    leaf_count,
    added_block,
    added_ordinal,
    to_timestamp(added_block * 30 + 1598306400) as added_at,
    removed_block,
    removed_ordinal,
    to_timestamp(removed_block * 30 + 1598306400) as removed_at,
    removed_by
from pieces
order by added_ordinal desc, piece_id desc
