with
    kentiks_location as (
        select
            provider as provider_id,
            agentcity as city,
            agentcountry as country,
            agentregion as region,
            agentlatitude as latitude,
            agentlongitude as longitude,
            latencyms as ping_latency
        from {{ ref("source_kentiks_storage_providers_location") }}
        qualify row_number() over (partition by provider order by date desc) = 1
    ),

    ipinfo_location as (
        select
            provider_id,
            ipinfo_city as city,
            ipinfo_country as country,
            ipinfo_region as region,
            ipinfo_latitude as latitude,
            ipinfo_longitude as longitude
        from {{ ref("source_statemarketdeals_active_miners_location") }}
        where ipinfo_country is not null
        qualify
            row_number() over (partition by provider_id order by updated_at desc) = 1
    ),

    synthetic_locations as (
        select provider_id, city, country, region, latitude, longitude,
        from {{ ref("source_jimpick_synthetic_storage_provider_location") }}
    ),

    joined_data as (
        select distinct
            coalesce(kl.provider_id, ipi.provider_id, sl.provider_id) as provider_id,
            coalesce(kl.city, ipi.city, sl.city) as city,
            coalesce(kl.country, ipi.country, sl.country) as country,
            coalesce(kl.region, ipi.region, sl.region) as region,
            coalesce(kl.latitude, ipi.latitude, sl.latitude) as latitude,
            coalesce(kl.longitude, ipi.longitude, sl.longitude) as longitude,
            kl.ping_latency,
            get_current_timestamp() as updated_at
        from kentiks_location as kl
        full outer join ipinfo_location as ipi on kl.provider_id = ipi.provider_id
        full outer join synthetic_locations as sl on kl.provider_id = sl.provider_id
    )

select provider_id, city, country, region, latitude, longitude, ping_latency, updated_at
from joined_data
qualify
    row_number() over (partition by provider_id order by updated_at desc) = 1

    -- TODO: deduplicate rows
    
