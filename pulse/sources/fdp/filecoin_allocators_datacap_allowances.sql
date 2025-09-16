select
    allowance_id,
    allocator_id,
    allowance_error,
    height,
    height_at,
    allowance_tibs,
    audit_trail,
    verifier_id,
    allowance_address_id,
    dc_source,
    audit_status,
    is_virtual,
    issue_created_at,
    message_created_at,
    message_cid
from 'https://data.filecoindataportal.xyz/filecoin_allocators_datacap_allowances.parquet'
