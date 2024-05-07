with source as (
    select
        height - 1 as height,
        to_timestamp(height * 30 + 1598306400)::timestamp as height_at,
        address as allocator_id,
        try_cast(data_cap as bigint) as datacap_bytes,
        try_cast(data_cap as bigint) / power(1024, 4) as datacap_tibs,
        event as event_type
    from {{ source("raw_assets", "raw_verified_registry_verifiers") }}
),

datacapstats_verifiers_allowances as (
    select
        addressId as allocator_id,
        aa ->> '$.allowanceArray.id' as allowance_id,
        aa ->> '$.allowanceArray.error' as allowance_error,
        try_cast(aa ->> '$.allowanceArray.height' as int) as height,
        aa ->> '$.allowanceArray.msgCID' as message_cid,
        aa ->> '$.allowanceArray.retries' as retries,
        aa ->> '$.allowanceArray.allowance' as allowance,
        aa ->> '$.allowanceArray.auditTrail' as audit_trail,
        aa ->> '$.allowanceArray.verifierId' as verifier_address_id,
        aa ->> '$.allowanceArray.issueCreateTimestamp' as issue_created_at,
        aa ->> '$.allowanceArray.createMessageTimestamp' as messaged_created_at
    from {{ source("raw_assets", "raw_datacapstats_verifiers") }}, unnest(allowanceArray) as aa
    qualify row_number() over (partition by allocator_id, message_cid order by height) = 1
    order by height desc
),

datacapstats_client_allowances as (
    select
      addressId as client_id,
      aa ->> '$.allowanceArray.id' as allowance_id,
      aa ->> '$.allowanceArray.error' as allowance_error,
      try_cast(aa ->> '$.allowanceArray.height' as int) as height,
      aa ->> '$.allowanceArray.msgCID' as message_cid,
      aa ->> '$.allowanceArray.retries' as retries,
      aa ->> '$.allowanceArray.allowance' as allowance,
      aa ->> '$.allowanceArray.auditTrail' as audit_trail,
      aa ->> '$.allowanceArray.allowanceTTD' as allowance_ttd,
      aa ->> '$.allowanceArray.isDataPublic' as is_data_public,
      aa ->> '$.allowanceArray.issueCreator' as issue_creator,
      aa ->> '$.allowanceArray.providerList' as provider_list,
      aa ->> '$.allowanceArray.usedAllowance' as used_allowance,
      aa ->> '$.allowanceArray.isLdnAllowance' as is_ldn_allowance,
      aa ->> '$.allowanceArray.isEFilAllowance' as is_efil_allowance,
      aa ->> '$.allowanceArray.verifierAddressId' as allocator_id,
      aa ->> '$.allowanceArray.isFromAutoverifier' as is_from_autoverifier,
      aa ->> '$.allowanceArray.retrievalFrequency' as retrieval_frequency,
      aa ->> '$.allowanceArray.searchedByProposal' as searched_by_proposal,
      aa ->> '$.allowanceArray.issueCreateTimestamp' as issue_created_at,
      aa ->> '$.allowanceArray.hasRemainingAllowance' as has_remaining_allowance,
      aa ->> '$.allowanceArray.createMessageTimestamp' as messaged_created_at,
  from {{ source("raw_assets", "raw_datacapstats_verified_clients") }}, unnest(allowanceArray) as aa
)

select
    s.height,
    s.height_at,
    s.allocator_id,
    s.event_type,
    datacap_bytes as remaining_datacap_bytes,
    datacap_tibs as remaining_datacap_tibs,
    lag(datacap_bytes) over (partition by s.allocator_id order by s.height asc) - remaining_datacap_bytes as datacap_allowance_change_bytes,
    datacap_allowance_change_bytes / power(1024, 4) as datacap_allowance_change_tibs,
    coalesce(dva.message_cid, dca.message_cid) as message_cid,
    coalesce(dca.audit_trail, dva.audit_trail) as audit_trail,
    coalesce(dca.issue_created_at, dva.issue_created_at) as issue_created_at,
    client_id,
    is_ldn_allowance,
    is_efil_allowance,
    is_from_autoverifier
from source as s
left join datacapstats_verifiers_allowances as dva on s.height = dva.height and s.allocator_id = dva.allocator_id
left join datacapstats_client_allowances as dca on s.height = dca.height and s.allocator_id = dca.allocator_id
order by s.height desc
