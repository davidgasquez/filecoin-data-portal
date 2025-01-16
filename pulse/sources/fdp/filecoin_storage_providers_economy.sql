select
    date,
    provider_id,
    balance,
    locked_funds,
    provider_collateral as collateral
from 'https://data.filecoindataportal.xyz/filecoin_daily_storage_providers_metrics.parquet'
where (balance is not null
   or locked_funds is not null
   or provider_collateral is not null)
   and date >= (current_date - interval '365 days')
order by provider_id desc, date desc
