with source as (
    select * from {{ source('raw_assets', 'raw_storage_providers_location_provider_quest') }}
)

select
    provider as provider_id,
    region,
    long as longitude,
    lat as latitude,
    country,
    city
from source
qualify row_number() over (partition by provider order by region desc) = 1
