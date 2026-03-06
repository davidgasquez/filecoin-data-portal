---
title: Storage Providers
---

_A quick view into Filecoin Storage Providers Metrics_

<Alert status="warning">
  <div>Pulse is being considered for deprecation.</div>
  <div>
    Prefer
    <a href="https://datacapstats.io/">DataCap Stats</a>,
    <a href="https://filecoin.tools/">Filecoin Tools</a>, or
    <a href="https://numbers.filecoindataportal.xyz/">Filecoin in Numbers</a>.
    If none of these fit your use case,
    <a href="https://github.com/davidgasquez/filecoin-data-portal/issues/new">open an issue</a>.
  </div>
</Alert>

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
