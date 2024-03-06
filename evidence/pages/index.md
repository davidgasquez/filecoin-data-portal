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
  onboarded_data_tibs,
  deals,
  unique_clients,
  unique_providers
from daily_metrics
where extract(year from date) like '${inputs.year}'
order by date desc
```

<LineChart
  data={daily_metrics}
  y=onboarded_data_tibs
  title = "Onboarded Data (TiBs)"
/>

<LineChart
  data={daily_metrics}
  y=deals
  title = "Unique onboarded Deals"
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
  sum(onboarded_data_tibs)
from provider_metrics
where extract(year from date) like '${inputs.year}'
group by provider_id, link
order by 3 desc
limit 20
```

<DataTable
    data={providers}
    link=link
/>
