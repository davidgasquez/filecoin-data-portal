select
    allowance_id,
    allocator_id,
    allowance_error,
    height,
    height_at,
    allowance_tibs,
    audit_trail,
    issue_created_at,
    messaged_created_at,
    message_cid,
from 'https://data.filecoindataportal.xyz/filecoin_allocators_datacap_allowances.parquet'
