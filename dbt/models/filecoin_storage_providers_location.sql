with source as (
    select * from {{ source('raw_assets', 'raw_storage_providers_location_provider_quest') }}
)

select
    {{ adapter.quote("provider") }} as provider_id,
    {{ adapter.quote("region") }},
    {{ adapter.quote("long") }} as longitude,
    {{ adapter.quote("lat") }} as latitude,
    {{ adapter.quote("country") }},
    {{ adapter.quote("city") }}
from source
qualify row_number() over (partition by {{ adapter.quote("provider") }}) = 1
