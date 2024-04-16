with base as (
    select
        stat_date::date as date,
        miner_id as provider_id,
        raw_byte_power as raw_power_bytes,
        raw_byte_power / 1024 ^ 5 as raw_power_pibs,
        quality_adj_power as quality_adjusted_power_bytes,
        quality_adj_power / 1024 ^ 5 as quality_adjusted_power_pibs,
        (quality_adjusted_power_bytes - raw_power_bytes) / 9 as verified_data_power_bytes,
        (quality_adjusted_power_pibs - raw_power_pibs) / 9 as verified_data_power_pibs,
    from {{ source('raw_assets', 'raw_storage_providers_daily_power') }}
)

select
    date,
    base.provider_id,
    raw_power_bytes,
    raw_power_pibs,
    quality_adjusted_power_bytes,
    quality_adjusted_power_pibs,
    verified_data_power_bytes,
    verified_data_power_pibs,
from base
order by date desc, raw_power_bytes desc
