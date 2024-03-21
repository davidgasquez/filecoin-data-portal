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
    *
from source
order by 1 desc
