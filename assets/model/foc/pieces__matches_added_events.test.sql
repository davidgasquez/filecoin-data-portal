-- Every added piece in the source events appears exactly once, and legacy id/CID arrays are aligned.
with events as (
    select
        cast(json_extract_string(args, '$.setId') as bigint) as data_set_id,
        block_number * 1000000 + log_index as added_ordinal,
        json_array_length(args -> '$.pieceCids') as cids,
        coalesce(json_array_length(args -> '$.pieceIds'), json_array_length(args -> '$.pieceCids')) as ids
    from raw.riba_eth_logs_decoded
    where contract_name = 'pdp_verifier'
      and event_name in ('PiecesAdded', 'PiecesAddedV2')
),
modeled as (
    select data_set_id, added_ordinal, count(*) as pieces
    from model.foc_pieces
    group by 1, 2
)
select *
from events
full join modeled using (data_set_id, added_ordinal)
where events.cids is distinct from events.ids
   or events.cids is distinct from modeled.pieces
