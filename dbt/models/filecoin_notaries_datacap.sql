with source as (
    select
        height,
        to_timestamp(height * 30 + 1598306400)::timestamp as updated_at,
        address as notary_id,
        data_cap as datacap,
        event as event_type
    from {{ source('raw_assets', 'raw_verified_registry_verifiers') }}
)

select
    height,
    updated_at,
    notary_id,
    try_cast(datacap as bigint) as datacap_bytes,
    try_cast(datacap as bigint) / power(1024, 4) as datacap_tibs,
    event_type
from source
order by 1 desc
