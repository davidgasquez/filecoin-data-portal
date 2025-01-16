select
    date,
    provider_id,
    raw_power_pibs,
    quality_adjusted_power_pibs
from 'https://data.filecoindataportal.xyz/filecoin_daily_storage_providers_metrics.parquet'
where 1=1
   and quality_adjusted_power_pibs > 0
   and date >= (current_date - interval '365 days')
order by date desc, quality_adjusted_power_pibs desc
