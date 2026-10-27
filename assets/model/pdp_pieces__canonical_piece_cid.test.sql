-- Re-encode each PieceCIDv2 (FRC-0069) from parsed padding/height and compare byte-for-byte.
-- Fails loudly on non-canonical uvarints, multi-byte multihash lengths, or any other layout drift.
with encoded as (
    select
        *,
        greatest(1, len(list_filter(range(10), lambda i: padding >> (7 * i) > 0))) as varint_bytes
    from model.pdp_pieces
)
select data_set_id, piece_id, piece_cid
from encoded
where piece_cid <> '0x01559120'
    || printf('%02x', varint_bytes + 33)
    || array_to_string(list_transform(
        range(varint_bytes),
        lambda i: printf('%02x', ((padding >> (7 * i)) & 127) | (case when i < varint_bytes - 1 then 128 else 0 end))
    ), '')
    || printf('%02x', height)
    || right(piece_cid, 64)
