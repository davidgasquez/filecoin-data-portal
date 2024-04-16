with source as (
    select
        addressId as allocator_id,
        address as allocator_address,
        auditTrail as audit_trail_url,
        nullif(trim(name), '') as allocator_name,
        orgName as allocator_organization_name,
        removed,
        initialAllowance::bigint as initial_allowance_bytes,
        initialAllowance::bigint / power(1024, 4) as initial_allowance_tibs,
        allowance::bigint as current_allowance_bytes,
        allowance::bigint / power(1024, 4) as current_allowance_tibs,
        isMultisig as is_multisig,
        createdAtHeight::int as created_at_height,
        to_timestamp(created_at_height * 30 + 1598306400)::timestamp as created_at,
        to_timestamp(issueCreateTimestamp)::timestamp as issue_created_at,
        verifiedClientsCount as verified_clients_count,
        receivedDatacapChange as received_datacap_change,
        allowanceArray as allowances,
        case when created_at_height > 3656949 then true else false end as is_active
    from {{ source('raw_assets', 'raw_datacapstats_verifiers') }}
)

select
    *
from source
