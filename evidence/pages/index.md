---
title: Filecoin Deals
---

_A quick view into Filecoin State Market Deals Metrics_

```sql years
select
  distinct extract(year from date) as year,
from daily_metrics
```

<Dropdown
  name=year
    data={years}
    value=year
>
  <DropdownOption value="%" valueLabel="All"/>
</Dropdown>


```sql daily_metrics
select
  date,
  proposed_data_tibs,
  proposed_deals,
  unique_clients,
  unique_providers
from daily_metrics
where extract(year from date) like '${inputs.year}'
order by date desc
```

<LineChart
  data={daily_metrics}
  y=proposed_data_tibs
  title = "Proposed Data (TiBs)"
/>

<LineChart
  data={daily_metrics}
  y=proposed_deals
  title = "Unique Proposed Deals"
/>

<LineChart
  data={daily_metrics}
  y=unique_clients
  title = "Unique Daily Clients"
/>
<LineChart
  data={daily_metrics}
  y=unique_providers
  title = "Unique Daily Providers"
/>

---

## Top Providers

```sql providers
select
  provider_id,
  '/provider/' || provider_id as link,
  proposed_data_tibs
from provider_metrics
order by 3 desc
limit 20
```

<DataTable
    data={providers}
    link=link
/>
