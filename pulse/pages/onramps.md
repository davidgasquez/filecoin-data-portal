---
title: Onramps
---

_A detailed view into Filecoin Onramps._


```sql onramps_stats
select
  count(distinct onramp_name) as total_onramps,
  sum(cast(total_deals as numeric)) as total_onramps_clients,
  sum(total_data_uploaded_tibs) as total_data_uploaded_tibs,
  sum(cast(total_deals as numeric)) as total_deals,
from filecoin_onramps
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
  total_deals as deals,
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
/>
