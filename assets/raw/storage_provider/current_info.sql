-- asset.description = Storage provider miner info from the latest miner info snapshot.
-- asset.resource = bigquery.lily

-- asset.column = provider_id | Filecoin storage provider miner actor id address.
-- asset.column = owner_id | Current owner id address from the snapshot.
-- asset.column = worker_id | Current worker id address from the latest snapshot.
-- asset.column = peer_id | Current libp2p peer id from the latest snapshot.
-- asset.column = control_addresses | Current JSON array of control addresses.
-- asset.column = multi_addresses | Current JSON array of multiaddrs.
-- asset.column = sector_size | Current sector size in bytes.

-- asset.not_null = provider_id
-- asset.not_null = sector_size
-- asset.unique = provider_id
-- asset.assert = sector_size > 0

select
    miner_id as provider_id,
    owner_id,
    worker_id,
    nullif(peer_id, '') as peer_id,
    nullif(control_addresses, '[]') as control_addresses,
    nullif(multi_addresses, '[]') as multi_addresses,
    cast(sector_size as int64) as sector_size
from `miner_infos`
where cast(sector_size as int64) > 0
qualify row_number() over (
    partition by miner_id
    order by height desc
) = 1
order by provider_id
