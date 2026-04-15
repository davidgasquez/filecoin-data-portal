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
        *
    from {{ ref('filecoin_allocators_datacap_allowances') }}
),

datacapstats_client_allowances as (
    select
        *
    from {{ ref('filecoin_clients_datacap_allowances') }}
)

select
    s.height,
    s.height_at,
    s.allocator_id,
    s.event_type,
    datacap_bytes as remaining_datacap_bytes,
    datacap_tibs as remaining_datacap_tibs,
    case when event_type = 'MODIFIED' then
        remaining_datacap_bytes - lag(datacap_bytes) over (partition by s.allocator_id order by s.height asc)
    else
        remaining_datacap_bytes
    end as datacap_allowance_change_bytes, -- only works if there is 1 ADDED event per Allocator
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
