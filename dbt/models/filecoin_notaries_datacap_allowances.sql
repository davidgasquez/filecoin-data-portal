with source as (
    select
        addressId as notary_id,
        aa ->> '$.allowanceArray.id' as allowance_id,
        aa ->> '$.allowanceArray.error' as allowance_error,
        aa ->> '$.allowanceArray.height' as height,
        aa ->> '$.allowanceArray.msgCID' as message_cid,
        aa ->> '$.allowanceArray.retries' as retries,
        aa ->> '$.allowanceArray.allowance' as allowance,
        aa ->> '$.allowanceArray.auditTrail' as audit_trail,
        aa ->> '$.allowanceArray.verifierId' as verifier_address_id,
        aa ->> '$.allowanceArray.issueCreateTimestamp' as issue_created_at,
        aa ->> '$.allowanceArray.createMessageTimestamp' as messaged_created_at
    from {{ source("raw_assets", "raw_datacapstats_verifiers") }}, unnest(allowanceArray) as aa
)

select
    allowance_id::numeric as allowance_id,
    notary_id,
    allowance_error,
    if(nullif(allowance_error, '') is null, true, false) as is_valid,
    height::numeric as height,
    to_timestamp(height::numeric * 30 + 1598306400)::timestamp as height_at,
    message_cid,
    retries,
    allowance::bigint as allowance_bytes,
    allowance::bigint / power(1024, 4) as allowance_tibs,
    audit_trail,
    verifier_address_id,
    to_timestamp(issue_created_at::numeric) as issue_created_at,
    to_timestamp(messaged_created_at::numeric) as messaged_created_at
from source
order by height desc
