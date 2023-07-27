with
    base as (
        select
            stat_date::date as date,
            miner_id as provider_id,
            raw_byte_power as raw_power_bytes,
            raw_byte_power / 1024 ^ 5 as raw_power_pibs,
            quality_adj_power as quality_adjusted_power_bytes,
            quality_adj_power / 1024 ^ 5 as quality_adjusted_power_pibs,
            (quality_adjusted_power_bytes - raw_power_bytes)
            / 9 as verified_data_power_bytes,
            (quality_adjusted_power_pibs - raw_power_pibs)
            / 9 as verified_data_power_pibs
        from {{ ref("source_spacescope_storage_provider_power") }}
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
    case
        when raw_power_pibs = 0
        then '=0'
        when raw_power_pibs < 0.1
        then '<0.1'
        when raw_power_pibs between 0.1 and 1
        then '>0.1<1'
        when raw_power_pibs between 1 and 10
        then '>1<10'
        when raw_power_pibs between 10 and 50
        then '>10<50'
        when raw_power_pibs > 50
        then '>50'
        else 'unknwon'
    end as raw_power_pibs_bucket,
    case
        when verified_data_power_pibs = 0
        then '=0'
        when verified_data_power_pibs < 0.1
        then '<0.1 '
        when verified_data_power_pibs < 1
        then '>0.1<1'
        when verified_data_power_pibs < 10
        then '>1<10'
        when verified_data_power_pibs > 50
        then '>50'
        else 'unknwon'
    end as verified_data_power_pibs_bucket,
    country,
    region
from base
left join
    filecoin_storage_providers_locations as spl on base.provider_id = spl.provider_id
order by date desc
