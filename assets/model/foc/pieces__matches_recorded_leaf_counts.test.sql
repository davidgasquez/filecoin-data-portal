-- Reconstructed live leaves must equal leafCount recorded by NextProvingPeriod and DataSetDeleted.
with deltas as (
    select data_set_id, added_ordinal as ordinal, leaf_count as leaves
    from model.foc_pieces
    union all
    select data_set_id, removed_ordinal, -leaf_count
    from model.foc_pieces
    where removed_ordinal is not null
),
state as (
    select
        data_set_id,
        ordinal,
        sum(sum(leaves)) over (partition by data_set_id order by ordinal) as leaves
    from deltas
    group by 1, 2
),
recorded as (
    select
        cast(json_extract_string(args, '$.setId') as bigint) as data_set_id,
        block_number * 1000000 + log_index as ordinal,
        event_name,
        cast(coalesce(
            json_extract_string(args, '$.leafCount'),
            json_extract_string(args, '$.deletedLeafCount')
        ) as hugeint) as recorded_leaves
    from raw.riba_eth_logs_decoded
    where contract_name = 'pdp_verifier'
      and event_name in ('NextProvingPeriod', 'DataSetDeleted')
)
select
    recorded.*,
    coalesce(state.leaves, 0) as reconstructed_leaves
from recorded
asof left join state
    on recorded.data_set_id = state.data_set_id
   and recorded.ordinal > state.ordinal
where recorded.recorded_leaves <> coalesce(state.leaves, 0)
