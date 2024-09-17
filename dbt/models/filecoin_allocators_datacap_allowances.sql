with source as (
    select
        addressId as allocator_id,
        aa ->> '$.unnest.id' as allowance_id,
        aa ->> '$.unnest.error' as allowance_error,
        aa ->> '$.unnest.height' as height,
        aa ->> '$.unnest.msgCID' as message_cid,
        aa ->> '$.unnest.retries' as retries,
        aa ->> '$.unnest.allowance' as allowance,
        aa ->> '$.unnest.auditTrail' as audit_trail,
        aa ->> '$.unnest.verifierId' as verifier_address_id,
        aa ->> '$.unnest.issueCreateTimestamp' as issue_created_at,
        aa ->> '$.unnest.createMessageTimestamp' as messaged_created_at
    from {{ source("raw_assets", "raw_datacapstats_verifiers") }}, unnest(allowanceArray) as aa
)

select
    allowance_id::numeric as allowance_id,
    allocator_id,
    allowance_error,
    height::numeric as height,
    to_timestamp(try_cast(height as numeric) * 30 + 1598306400)::timestamp as height_at,
    message_cid,
    retries,
    allowance::bigint as allowance_bytes,
    allowance::bigint / power(1024, 4) as allowance_tibs,
    audit_trail,
    verifier_address_id,
    to_timestamp(try_cast(issue_created_at as numeric)) as issue_created_at,
    to_timestamp(messaged_created_at::numeric) as messaged_created_at
from source
qualify row_number() over (partition by message_cid, height order by height desc) = 1
order by height desc
