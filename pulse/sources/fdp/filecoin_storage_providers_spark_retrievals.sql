select
    date,
    provider_id,
    spark_retrieval_success_rate,
from 'https://data.filecoindataportal.xyz/filecoin_daily_storage_providers_metrics.parquet'
where 1=1
   and spark_retrieval_success_rate is not null
   and date >= (current_date - interval '365 days')
order by date desc, spark_retrieval_success_rate desc
