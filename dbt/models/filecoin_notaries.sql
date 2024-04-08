with source as (
    select
        addressId as notary_id,
        address as notary_address,
        auditTrail as audit_trail_url,
        nullif(trim(name), '') as notary_name,
        orgName as notary_organization_name,
        removed,
        initialAllowance::bigint as initial_allowance_bytes,
        initialAllowance::bigint / power(1024, 4) as initial_allowance_tibs,
        allowance::bigint as current_allowance_bytes,
        allowance::bigint / power(1024, 4) as current_allowance_tibs,
        isMultisig as is_multisig,
        createdAtHeight as created_at_height,
        to_timestamp(created_at_height * 30 + 1598306400)::timestamp as created_at,
        to_timestamp(issueCreateTimestamp)::timestamp as issue_created_at,
        verifiedClientsCount as verified_clients_count,
        receivedDatacapChange as received_datacap_change,
        allowanceArray as allowances
    from {{ source('raw_assets', 'raw_datacapstats_verifiers') }}
)

select
    *
from source
