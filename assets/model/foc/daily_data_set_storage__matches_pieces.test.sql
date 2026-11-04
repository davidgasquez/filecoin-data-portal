-- Latest sparse states must equal live PDP pieces, using unique transaction pairs.
with creations as (
    select transaction_hash as tx,
        count(*) filter (where contract_name = 'filecoin_warm_storage_service') as fwss_count,
        count(*) filter (where contract_name = 'pdp_verifier') as pdp_count,
        max(cast(args ->> 'dataSetId' as bigint)) filter (
            where contract_name = 'filecoin_warm_storage_service'
        ) as data_set_id,
        max(cast(args ->> 'setId' as bigint)) filter (where contract_name = 'pdp_verifier') as set_id
    from raw.riba_eth_logs_decoded
    where event_name = 'DataSetCreated'
      and contract_name in ('filecoin_warm_storage_service', 'pdp_verifier')
    group by 1
),
expected as (
    select m.data_set_id, count(*) as pieces, sum(p.raw_size_bytes) as bytes
    from creations m
    join model.foc_pieces p on p.data_set_id = m.set_id
    cross join (
        select max(checkpoint_ordinal) as ordinal from model.network_daily_fevm_checkpoints
        where date < current_date
    ) c
    where m.fwss_count = 1 and m.pdp_count = 1
      and p.added_ordinal <= c.ordinal
      and (p.removed_ordinal is null or p.removed_ordinal > c.ordinal)
    group by 1
),
actual as (
    select * from model.foc_daily_data_set_storage
    qualify row_number() over (partition by data_set_id order by date desc) = 1
)
select coalesce(a.data_set_id, e.data_set_id) as data_set_id
from actual a full join expected e using (data_set_id)
where coalesce(a.stored_pieces, 0) != coalesce(e.pieces, 0)
   or coalesce(a.stored_bytes, 0) != coalesce(e.bytes, 0)
union all
select data_set_id from model.foc_daily_data_set_storage group by date, data_set_id having count(*) > 1
