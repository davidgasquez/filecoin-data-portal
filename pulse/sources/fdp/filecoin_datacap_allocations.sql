select
    height,
    height_at,
    allocator_id,
    event_type,
    remaining_datacap_tibs,
    datacap_allowance_change_tibs,
    message_cid
from 'https://data.filecoindataportal.xyz/filecoin_datacap_allocations.parquet'
