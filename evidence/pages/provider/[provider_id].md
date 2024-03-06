# {$page.params.provider_id}

```sql filtered_provider_metrics
select
  *
from provider_metrics
where provider_id = '${params.provider_id}'
```

<DataTable data={filtered_provider_metrics}/>

<BarChart
  data={filtered_provider_metrics}
  y=onboarded_data_tibs
  title = "Onboarded Data (TiBs)"
/>
