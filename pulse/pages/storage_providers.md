---
title: Storage Providers
---

_A quick view into Filecoin Storage Providers Metrics_

## Explorer

<BigLink href='https://docs.google.com/spreadsheets/d/1hC5HwuiqQvQcVvV06n3SH0wKkZwbw20EufGYHSyENs0'>
  Explore Storage Providers on Google Sheets
</BigLink>

```sql providers
select
  provider_id,
  '/provider/' || provider_id as link,
  total_active_deals,
  total_data_uploaded_tibs,
  total_active_data_uploaded_tibs,
  total_unique_clients,
  first_deal_at,
  last_deal_at,
  country,
  provider_name
from filecoin_storage_providers
where 1 = 1
  -- and (last_deal_at > '2023-06-01' or data_uploaded_tibs_30d > 0 or provider_name is not null)
order by total_active_data_uploaded_tibs desc, data_uploaded_tibs_30d desc
```

<DataTable
  data={providers}
  link=link
  search=true
  rows=20
  rowShading=true
  rowLines=false
  downloadable=true
/>


## Retrievals

```sql retrieval_stats
with retrievals as (
  select
    provider_id,
    spark_retrieval_success_rate
  from filecoin_storage_providers_spark_retrievals
  where date = (select max(date) from filecoin_storage_providers_spark_retrievals)
)

select
  count(distinct provider_id) as total_tested_providers,
  avg(spark_retrieval_success_rate) as avg_success_rate,
  count(distinct provider_id) filter (where spark_retrieval_success_rate > 0) as providers_with_success,
  providers_with_success / total_tested_providers as providers_with_success_rate
from retrievals
where spark_retrieval_success_rate is not null
```

<Grid cols=2>

<BigValue
  data={retrieval_stats}
  value=total_tested_providers
/>

<BigValue
  data={retrieval_stats}
  value=avg_success_rate
  fmt='0.00%'
/>

<BigValue
  data={retrieval_stats}
  value=providers_with_success
/>

<BigValue
  data={retrieval_stats}
  value=providers_with_success_rate
  fmt='0.00%'
/>

</Grid>

### Providers Retrieval Leaderboard

```sql top_retrieval_providers
select
  provider_id,
  spark_retrieval_success_rate,
  '/provider/' || provider_id as link,
from filecoin_storage_providers_spark_retrievals
where date = (select max(date) from filecoin_storage_providers_spark_retrievals) and spark_retrieval_success_rate > 0
order by spark_retrieval_success_rate desc
```

<DataTable
  data={top_retrieval_providers}
  link=link
  rows=10
  rowNumbers=true
/>

```sql cdf_spark
WITH ranked_data AS (
  SELECT
    mean_spark_retrieval_success_rate_7d,
    ROW_NUMBER() OVER (ORDER BY mean_spark_retrieval_success_rate_7d) AS row_num,
    COUNT(*) OVER () AS total_rows
  FROM
    filecoin_storage_providers
  WHERE
    mean_spark_retrieval_success_rate_7d IS NOT NULL
)
SELECT
  mean_spark_retrieval_success_rate_7d,
  (row_num / total_rows::FLOAT) AS cdf
FROM
  ranked_data
ORDER BY
  mean_spark_retrieval_success_rate_7d
```

### Providers Retrieval Success Rate CDF

Cumulative Distribution Function (CDF) of the average Spark Retrieval Success Rate of all tesed providers.

<LineChart
  data={cdf_spark}
  x=mean_spark_retrieval_success_rate_7d
  y=cdf
  yMin=0
  yMax=1
  handleMissing=connect
  yFmt='0%'
  emptySet=pass
/>
