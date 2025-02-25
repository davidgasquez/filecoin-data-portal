---
title: Filecoin Pulse
---

_A view into the Filecoin Network. Powered by the [Filecoin Data Portal](https://filecoindataportal.xyz/)._

<DateRange
  name=date_filter
  start=2020-09-01
  defaultValue={'Last 365 Days'}
/>

```sql metrics
select
  date,
  data_on_active_deals_pibs,
  data_on_active_deals_pibs - lag(data_on_active_deals_pibs, 1) over (order by date) as data_on_active_deals_pibs_mom,
  active_deals,
  active_deals - lag(active_deals, 1) over (order by date) as active_deals_mom,
  clients_with_active_deals,
  clients_with_active_deals - lag(clients_with_active_deals, 1) over (order by date) as clients_with_active_deals_mom,
  providers_with_active_deals,
  providers_with_active_deals - lag(providers_with_active_deals, 1) over (order by date) as providers_with_active_deals_mom,
  active_address_count_daily,
  active_address_count_daily - lag(active_address_count_daily, 1) over (order by date) as active_address_count_daily_mom,
  raw_power_pibs,
  raw_power_pibs - lag(raw_power_pibs, 1) over (order by date) as raw_power_pibs_mom,
  quality_adjusted_power_pibs,
  quality_adjusted_power_pibs - lag(quality_adjusted_power_pibs, 1) over (order by date) as quality_adjusted_power_pibs_mom,
  verified_data_power_pibs,
  network_utilization_ratio,
  network_utilization_ratio - lag(network_utilization_ratio, 1) over (order by date) as network_utilization_ratio_mom,
  onboarded_data_pibs,
  unique_deal_making_clients,
  unique_deal_making_providers,
  active_address_count_monthly,
  new_provider_ids,
  new_client_ids
from filecoin_monthly_metrics
where date between '${inputs.date_filter.start}' and '${inputs.date_filter.end}'
order by date desc
```

<Grid cols=4>

<BigValue
  title="Data on Active Deals"
  value=data_on_active_deals_pibs
  data={metrics}
  comparison=data_on_active_deals_pibs_mom
  comparisonTitle="MoM"
  fmt="pibs"
/>

<BigValue
  title="Active Deals"
  data={metrics}
  value=active_deals
  comparison=active_deals_mom
  comparisonTitle="MoM"
/>

<BigValue
  title="Clients with Active Deals"
  data={metrics}
  value=clients_with_active_deals
  comparison=clients_with_active_deals_mom
  comparisonTitle="MoM"
/>

<BigValue
  title="Providers with Active Deals"
  data={metrics}
  value=providers_with_active_deals
  comparison=providers_with_active_deals_mom
  comparisonTitle="MoM"
/>

<BigValue
  title="Daily Active Addresses"
  data={metrics}
  value=active_address_count_daily
  comparison=active_address_count_daily_mom
  comparisonTitle="MoM"
/>

<BigValue
  title="Raw Power"
  data={metrics}
  value=raw_power_pibs
  comparison=raw_power_pibs_mom
  comparisonTitle="MoM"
  fmt="pibs"
/>

<BigValue
  title="Quality Adjusted Power"
  data={metrics}
  value=quality_adjusted_power_pibs
  comparison=quality_adjusted_power_pibs_mom
  comparisonTitle="MoM"
  fmt="pibs"
/>

<BigValue
  title="Network Utilization"
  data={metrics}
  value=network_utilization_ratio
  comparison=network_utilization_ratio_mom
  comparisonTitle="MoM"
  fmt='00.0%'
/>

</Grid>

---

<BarChart
  data={metrics}
  x=date
  y=onboarded_data_pibs
  title="Data Onboarding"
  xFmt='MMM YYYY'
  yFmt="pibs"
/>

<Grid cols=2>

<BarChart
  data={metrics}
  x="date"
  y="unique_deal_making_clients"
  xFmt='MMM YYYY'
  title="Clients Making Deals"
/>

<BarChart
  data={metrics}
  x="date"
  y="clients_with_active_deals"
  xFmt='MMM YYYY'
  title="Clients With Active Deals"
/>

<BarChart
  data={metrics}
  x="date"
  y="unique_deal_making_providers"
  xFmt='MMM YYYY'
  title="Providers Making Deals"
/>

<BarChart
  data={metrics}
  x="date"
  y="providers_with_active_deals"
  xFmt='MMM YYYY'
  title="Providers With Active Deals"
/>

<BarChart
  data={metrics}
  x="date"
  y="active_address_count_monthly"
  xFmt='MMM YYYY'
  title="Active Address Count Monthly"
/>

<BarChart
  data={metrics}
  x="date"
  y={["new_provider_ids", "new_client_ids"]}
  legend=false
  xFmt='MMM YYYY'
  title="New Provider and Client IDs"
/>

</Grid>

<Grid cols=3>

<AreaChart
  data={metrics}
  x="date"
  y="raw_power_pibs"
  xFmt='MMM YYYY'
  title="Raw Power"
  fmt="pibs"
/>

<AreaChart
  data={metrics}
  x="date"
  y="quality_adjusted_power_pibs"
  xFmt='MMM YYYY'
  title="Quality Adjusted Power"
  fmt="pibs"
/>

<AreaChart
  data={metrics}
  x="date"
  y="verified_data_power_pibs"
  xFmt='MMM YYYY'
  title="Verified Data Power"
  fmt="pibs"
/>

</Grid>

<LastRefreshed/>

---

<Grid cols=2>

<LinkButton url='https://numbers.filecoindataportal.xyz/'>
  <p style="font-size: 1.3rem; text-align: center; margin: 0.5rem 0;">
    Filecoin In Numbers
  </p>
</LinkButton>

<LinkButton url='https://filecoindataportal.xyz/'>
  <p style="font-size: 1.3rem; text-align: center; margin: 0.5rem 0;">
    Filecoin Data Portal
  </p>
</LinkButton>

</Grid>
