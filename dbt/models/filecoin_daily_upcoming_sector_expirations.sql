with base as (
    select
        expiration_date,
        sector_count,
        cast(raw_power_bytes as decimal(38, 0)) as raw_power_bytes,
        cast(quality_adjusted_power_bytes as decimal(38, 9)) as quality_adjusted_power_bytes,
        cast(deal_weight as decimal(38, 0)) as deal_weight,
        cast(verified_deal_weight as decimal(38, 0)) as verified_deal_weight,
        cast(initial_pledge_attofil as decimal(38, 0)) as initial_pledge_attofil,
        cast(expected_day_reward_attofil as decimal(38, 0)) as expected_day_reward_attofil,
        cast(expected_storage_pledge_attofil as decimal(38, 0)) as expected_storage_pledge_attofil
    from {{ source('raw_assets', 'raw_filecoin_daily_upcoming_sector_expirations') }}
)

select
    expiration_date,
    sector_count,
    raw_power_bytes,
    raw_power_bytes / pow(1024, 5) as raw_power_pibs,
    quality_adjusted_power_bytes,
    quality_adjusted_power_bytes / pow(1024, 5) as quality_adjusted_power_pibs,
    deal_weight,
    verified_deal_weight,
    initial_pledge_attofil,
    initial_pledge_attofil / pow(10, 18) as initial_pledge_fil,
    expected_day_reward_attofil,
    expected_day_reward_attofil / pow(10, 18) as expected_day_reward_fil,
    expected_storage_pledge_attofil,
    expected_storage_pledge_attofil / pow(10, 18) as expected_storage_pledge_fil
from base
where expiration_date >= current_date()
    and expiration_date <= current_date() + interval 2 year
order by 1
