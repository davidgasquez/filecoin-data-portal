-- Every PDP piece needs exactly one data set creation (its storage provider) before its addition.
with created as (
    select
        cast(json_extract_string(args, '$.setId') as bigint) as data_set_id,
        block_number * 1000000 + log_index as ordinal
    from raw.riba_eth_logs_decoded
    where contract_name = 'pdp_verifier'
      and event_name = 'DataSetCreated'
)
select pieces.data_set_id, pieces.piece_id, count(created.ordinal) as creations
from model.foc_pieces as pieces
left join created
    on pieces.data_set_id = created.data_set_id
    and created.ordinal < pieces.added_ordinal
group by 1, 2
having count(created.ordinal) != 1
