---
title: Onramps
---

_A detailed view into Filecoin Onramps._

<Alert status="info">
  Deals data comes from State Market Deals. DDO deals are not incorporated.
</Alert>

```sql onramps_stats
select
  count(distinct onramp_name) as total_onramps,
  sum(cast(total_known_clients as numeric)) as total_onramps_clients,
  sum(total_data_uploaded_tibs) as total_data_uploaded_tibs,
  sum(cast(total_deals as numeric)) as total_deals,
from filecoin_onramps
where onramp_name != 'No Onramp'
```

<Grid cols=2>

<BigValue
  data={onramps_stats}
  value=total_onramps
  title="Filecoin Onramps"
/>

<BigValue
  data={onramps_stats}
  value=total_onramps_clients
  title="Total Onramps Clients"
/>

<BigValue
  data={onramps_stats}
  value=total_data_uploaded_tibs
  title="Total Data Uploaded"
/>

<BigValue
  data={onramps_stats}
  value=total_deals
  title="Total Deals"
/>

</Grid>

```sql onramps_table
select
  onramp_name as name,
  '/onramp/' || onramp_name as link,
  total_deals as deals,
  total_known_clients as known_clients,
  total_data_uploaded_tibs as data_uploaded_tibs,
  data_uploaded_tibs_6m as data_uploaded_tibs_6m,
  data_expired_tibs_6m as data_expired_tibs_6m,
  data_uploaded_tibs_1y as data_uploaded_tibs_1y,
  data_expired_tibs_1y as data_expired_tibs_1y,
from filecoin_onramps
order by data_uploaded_tibs_6m desc
```

## Explorer

<DataTable
  data={onramps_table}
  rowShading=true
  rowLines=false
  rows=30
  downloadable=true
  link=link
/>

## Daily Metrics

<DateRange
  name=date_filter
  start=2023-01-01
  defaultValue={'Last 365 Days'}
/>


```sql onramps_daily_metrics
select
  date,
  onramp_name,
  onboarded_data_tibs,
  deals
from filecoin_onramps_daily_metrics
where date between '${inputs.date_filter.start}' and '${inputs.date_filter.end}'
```

<BarChart
  data={onramps_daily_metrics}
  x=date
  y=onboarded_data_tibs
  yAxisTitle="Data Uploaded (TiBs)"
  title="Daily Data Uploaded"
  series=onramp_name
/>

<BarChart
  data={onramps_daily_metrics}
  x=date
  y=deals
  yAxisTitle="Deals"
  title="Daily Deals"
  series=onramp_name
/>
