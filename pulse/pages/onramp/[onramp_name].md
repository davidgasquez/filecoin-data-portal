# {$page.params.onramp_name}

<DateRange
  name=range
  start=2023-01-01
  defaultValue={'Last 365 Days'}
/>

```sql filtered_onramp
select
  *
from filecoin_onramps
where onramp_name = '${params.onramp_name}'
```

<Grid cols=3>

<BigValue
  data={filtered_onramp}
  value=onramp_name
  title="Name"
/>

<BigValue
  data={filtered_onramp}
  value=total_deals
  title="Deals"
/>

<BigValue
  data={filtered_onramp}
  value=total_data_uploaded_tibs
  title="Data Uploaded (TiBs)"
/>

<BigValue
  data={filtered_onramp}
  value=known_client_ids
  title="Client IDs"
/>

<BigValue
  data={filtered_onramp}
  value=total_verified_deals
  title="Verified Deals"
/>

<BigValue
  data={filtered_onramp}
  value=total_active_deals
  title="Active Deals"
/>

<BigValue
  data={filtered_onramp}
  value=total_active_verified_deals
  title="Active Verified Deals"
/>

<BigValue
  data={filtered_onramp}
  value=total_active_data_uploaded_tibs
  title="Active Data (TiBs)"
/>

<BigValue
  data={filtered_onramp}
  value=data_uploaded_tibs_30d
  title="Uploaded Last 30d (TiBs)"
/>

<BigValue
  data={filtered_onramp}
  value=data_uploaded_tibs_6m
  title="Uploaded Last 6m (TiBs)"
/>

<BigValue
  data={filtered_onramp}
  value=data_uploaded_tibs_1y
  title="Uploaded Last 1y (TiBs)"
/>

<BigValue
  data={filtered_onramp}
  value=data_expired_tibs_30d
  title="Expired Last 30d (TiBs)"
/>

<BigValue
  data={filtered_onramp}
  value=data_expired_tibs_6m
  title="Expired Last 6m (TiBs)"
/>

<BigValue
  data={filtered_onramp}
  value=data_expired_tibs_1y
  title="Expired Last 1y (TiBs)"
/>

<BigValue
  data={filtered_onramp}
  value=first_deal_at
  title="First Deal"
/>

<BigValue
  data={filtered_onramp}
  value=first_active_deal_at
  title="First Active Deal"
/>

<BigValue
  data={filtered_onramp}
  value=last_deal_at
  title="Last Deal"
/>

<BigValue
  data={filtered_onramp}
  value=last_active_deal_at
  title="Last Active Deal"
/>
</Grid>

## Metrics

```sql onramps_daily_metrics
select
  date,
  onboarded_data_tibs,
  deals
from filecoin_onramps_daily_metrics
where onramp_name = '${params.onramp_name}'
  and date between '${inputs.range.start}' and '${inputs.range.end}'
order by date desc
```

<CalendarHeatmap
  data={onramps_daily_metrics}
  date=date
  value=onboarded_data_tibs
  title="Onboarding Data (TiBs)"
/>

<Grid cols=2>
<LineChart
  data={onramps_daily_metrics}
  x=date
  y=onboarded_data_tibs
  title="Daily Data Onboarded (TiBs)"
/>

<BarChart
  data={onramps_daily_metrics}
  x=date
  y=deals
  title="Daily Deals"
/>
</Grid>
<DataTable
  data={onramps_daily_metrics}
  title="Daily Metrics"
/>
