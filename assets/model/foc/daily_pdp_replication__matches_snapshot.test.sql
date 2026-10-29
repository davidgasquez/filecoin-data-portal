-- Independently reconcile the event-delta totals with a direct latest-checkpoint snapshot.
with checkpoint as (
    select date, checkpoint_ordinal
    from model.network_daily_fevm_checkpoints
    where checkpoint_ordinal >= (select min(added_ordinal) from model.foc_pieces)
    order by date desc
    limit 1
),
providers as (
    select
        cast(args ->> '$.setId' as bigint) as data_set_id,
        arg_max(lower(case when event_name = 'DataSetCreated' then args ->> '$.storageProvider'
            else args ->> '$.newStorageProvider' end), block_number * 1000000 + log_index) as provider
    from raw.riba_eth_logs_decoded
    cross join checkpoint
    where contract_name = 'pdp_verifier'
      and event_name in ('DataSetCreated', 'StorageProviderChanged')
      and block_number * 1000000 + log_index <= checkpoint_ordinal
    group by 1
),
cids as (
    select
        pieces.piece_cid,
        max(pieces.raw_size_bytes) as bytes,
        count(*) as entries,
        count(distinct providers.provider) as providers
    from model.foc_pieces as pieces
    cross join checkpoint
    left join providers using (data_set_id)
    where pieces.added_ordinal <= checkpoint_ordinal
      and (pieces.removed_ordinal is null or pieces.removed_ordinal > checkpoint_ordinal)
    group by 1
),
expected as (
    select
        coalesce(sum(bytes * entries), 0) as registered_bytes,
        coalesce(sum(bytes), 0) as unique_bytes,
        coalesce(sum(bytes) filter (where providers >= 2), 0) as replicated_bytes
    from cids
)
select
    checkpoint.date,
    actual.registered_bytes,
    expected.registered_bytes as expected_registered_bytes,
    actual.unique_bytes,
    expected.unique_bytes as expected_unique_bytes,
    actual.replicated_bytes,
    expected.replicated_bytes as expected_replicated_bytes,
    actual.replication_coverage
from checkpoint
cross join expected
left join model.foc_daily_pdp_replication as actual using (date)
where actual.registered_bytes is distinct from expected.registered_bytes
   or actual.unique_bytes is distinct from expected.unique_bytes
   or actual.replicated_bytes is distinct from expected.replicated_bytes
   or actual.replication_coverage is distinct from expected.replicated_bytes / nullif(expected.unique_bytes, 0)
