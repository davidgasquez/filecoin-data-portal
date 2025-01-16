select
    date,
    provider_id,
    daily_sector_onboarding_count,
    daily_new_sector_terminated_raw_power_tibs,
    daily_new_sector_fault_raw_power_tibs,
    daily_new_sector_recover_raw_power_tibs,
    daily_new_sector_expire_raw_power_tibs,
    daily_new_sector_extend_raw_power_tibs,
    daily_new_sector_snap_raw_power_tibs
from 'https://data.filecoindataportal.xyz/filecoin_daily_storage_providers_metrics.parquet'
where 1=1
   and date >= (current_date - interval '365 days')
order by date desc
