-- Missing or malformed provider identities must not count as another holder.
select event_name, block_number, log_index, args
from raw.riba_eth_logs_decoded
where contract_name = 'pdp_verifier'
  and event_name in ('DataSetCreated', 'StorageProviderChanged')
  and not regexp_full_match(lower(coalesce(
      case when event_name = 'DataSetCreated' then args ->> '$.storageProvider'
          else args ->> '$.newStorageProvider' end,
      ''
  )), '0x[0-9a-f]{40}')
