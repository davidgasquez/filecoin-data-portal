with
    source as (select * from {{ source("state_market_deals", "active_miners") }}),

    renamed as (
        select
            minerid as miner_id,
            rawbytepower as raw_byte_power,
            qualityadjpower as quality_adjusted_power,
            geolite2country as geolite_country,
            geolite2region as geolite_region,
            geolite2city as geolite_city,
            geolite2metro as geolite_metro,
            geolite2latitude as geolite_latitude,
            geolite2longitude as geolite_longitude,
            geolite2timezone as geolite_timezone,
            geolite2radius as geolite_radius,
            ipinfocity as ipinfo_city,
            ipinforegion as ipinfo_region,
            ipinfocountry as ipinfo_country,
            ipinfolatitude as ipinfo_latitude,
            ipinfolongitude as ipinfo_longitude,
            ipinfoorg as ipinfo_org,
            ipinfopostal as ipinfo_postal,
            ipinfotimezone as ipinfo_timezone,
            ipinfohostname as ipinfo_hostname,
            createdat as created_at,
            updatedat as updated_at,
        from source
    )

select *
from renamed
