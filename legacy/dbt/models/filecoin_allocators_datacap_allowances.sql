{{ config(materialized='create_or_replace_table') }}

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
        aa ->> '$.unnest.verifierId' as verifier_id,
        aa ->> '$.unnest.dcSource' as dc_source,
        aa ->> '$.unnest.addressId' as allowance_address_id,
        aa ->> '$.unnest.auditStatus' as audit_status,
        aa ->> '$.unnest.isVirtual' as is_virtual,
        aa ->> '$.unnest.issueCreateTimestamp' as issue_created_at,
        aa ->> '$.unnest.createMessageTimestamp' as messaged_created_at
    from {{ source("raw_assets", "raw_datacapstats_verifiers") }}, unnest(allowanceArray) as aa
),

parsed as (
    select
        try_cast(allowance_id as numeric) as allowance_id,
        allocator_id,
        allowance_error,
        try_cast(height as numeric) as height,
        message_cid,
        retries,
        try_cast(allowance as bigint) as allowance_bytes,
        audit_trail,
        allowance_address_id,
        dc_source,
        audit_status,
        is_virtual,
        try_cast(verifier_id as numeric) as verifier_id,
        to_timestamp(try_cast(issue_created_at as numeric)) as issue_created_at,
        to_timestamp(try_cast(messaged_created_at as numeric)) as messaged_created_at
    from source
)

select
    allowance_id,
    allocator_id,
    allowance_error,
    height,
    to_timestamp(height * 30 + 1598306400)::timestamp as height_at,
    message_cid,
    retries,
    allowance_bytes,
    allowance_bytes / power(1024, 4) as allowance_tibs,
    audit_trail,
    allowance_address_id,
    dc_source,
    audit_status,
    is_virtual,
    verifier_id,
    issue_created_at,
    messaged_created_at
from parsed
where height is not null
qualify row_number() over (partition by message_cid, height order by height desc) = 1
order by height desc
