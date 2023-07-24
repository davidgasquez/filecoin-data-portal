with
    base as (
        select
            stat_date::date as date,
            miner_id as provider_id,
            raw_byte_power,
            raw_byte_power / 1024 ^ 5 as raw_pib_power,
            quality_adj_power quality_adjusted_byte_power,
            quality_adj_power / 1024 ^ 5 as quality_adjusted_pib_power,
        from {{ ref("source_spacescope_storage_provider_power") }}
    )

select
    date,
    base.provider_id,
    raw_byte_power,
    raw_pib_power,
    quality_adjusted_byte_power,
    quality_adjusted_pib_power,
    country
from base
left join
    filecoin_storage_providers_locations as spl on base.provider_id = spl.provider_id
order by date desc
