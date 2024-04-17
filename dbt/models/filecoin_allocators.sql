with datacapstats_allocators as (
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
),

datacap_allocators_registry as (
    select
        application_number,
        address as allocator_address,
        name as allocator_name,
        organization as allocator_organization_name,
        location,
        status,
        metapathway_type,
        associated_org_addresses,
        application,
        poc,
        pathway_addresses
    from  {{ source('raw_assets', 'raw_datacap_allocators_registry') }}
)

select
    da.allocator_id,
    da.allocator_address,
    da.audit_trail_url,
    coalesce(da.allocator_name, dar.allocator_name) as allocator_name,
    coalesce(da.allocator_organization_name, dar.allocator_organization_name) as allocator_organization_name,
    da.initial_allowance_bytes,
    da.initial_allowance_tibs,
    da.current_allowance_bytes,
    da.current_allowance_tibs,
    da.is_multisig,
    da.created_at_height,
    da.created_at,
    da.issue_created_at,
    da.verified_clients_count,
    da.received_datacap_change,
    -- da.allowances,
    da.is_active,
    dar.location,
    dar.status,
    dar.metapathway_type,
    dar.associated_org_addresses,
    dar.application,
    dar.poc,
    dar.pathway_addresses
from datacapstats_allocators as da
left join datacap_allocators_registry as dar
    on da.allocator_address = dar.allocator_address
order by created_at_height desc
