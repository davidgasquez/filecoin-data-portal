with provider_locations_json as (
    select
        unnest(providerlocations) as l
    from read_json_auto('https://geoip.feeds.provider.quest/synthetic-locations-latest.json')
)

select
    l ->> '$.provider' as provider_id,
    l ->> '$.city' as city,
    l ->> '$.country' as country,
    l ->> '$.region' as region,
    l ->> '$.long' as longitude,
    l ->> '$.lat' as latitude
from provider_locations_json
