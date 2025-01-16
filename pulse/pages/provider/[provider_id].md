# {$page.params.provider_id}

<DateRange
  name=range
  defaultValue={'Last 365 Days'}
/>

```sql filtered_provider_info
select
  *
from filecoin_storage_providers
where provider_id = '${params.provider_id}'
```

<Grid cols=4>

<BigValue
  data={filtered_provider_info}
  value=provider_name
  title="Name"
/>

<BigValue
  data={filtered_provider_info}
  value=total_deals
  title="Total Deals"
/>

<BigValue
  data={filtered_provider_info}
  value=total_active_deals
  title="Total Active Deals"
/>

<BigValue
  data={filtered_provider_info}
  value=total_data_uploaded_tibs
  title="Total Onboarded Data (TiBs)"
/>

<BigValue
  data={filtered_provider_info}
  value=unique_data_uploaded_tibs
  title="Unique Onboarded Data (TiBs)"
/>

<BigValue
  data={filtered_provider_info}
  value=unique_data_uploaded_ratio
  title="Unique Onboarded Data Ratio"
  fmt='#,##0.00%'
/>

<BigValue
  data={filtered_provider_info}
  value=data_uploaded_tibs_30d
  title="Onboarded Data (TiBs) last 30d"
/>

<BigValue
  data={filtered_provider_info}
  value=data_uploaded_tibs_6m
  title="Onboarded Data (TiBs) last 6m"
/>

<BigValue
  data={filtered_provider_info}
  value=data_uploaded_tibs_1y
  title="Onboarded Data (TiBs) last 1y"
/>

<BigValue
  data={filtered_provider_info}
  value=raw_power_pibs
  title="Raw Power (PiBs)"
/>

<BigValue
  data={filtered_provider_info}
  value=quality_adjusted_power_pibs
  title="Quality Adjusted Power (PiBs)"
/>

<BigValue
  data={filtered_provider_info}
  value=verified_data_power_pibs
  title="Verified Data Power (PiBs)"
/>

<BigValue
  data={filtered_provider_info}
  value=first_deal_at
  title="First Deal"
/>

<BigValue
  data={filtered_provider_info}
  value=last_deal_at
  title="Last Deal"
/>

<BigValue
  data={filtered_provider_info}
  value=country
  title="Country"
/>

<BigValue
  data={filtered_provider_info}
  value=is_reachable
  title="Is Reachable"
/>

<BigValue
  data={filtered_provider_info}
  value=filrep_uptime_average
  title="FilRepUptime Average"
/>

<BigValue
  data={filtered_provider_info}
  value=filrep_score
  title="FilRep Score"
/>

<BigValue
  data={filtered_provider_info}
  value=total_rewards
  title="Total Rewards (FIL)"
/>

<BigValue
  data={filtered_provider_info}
  value=total_blocks_mined
/>

<BigValue
  data={filtered_provider_info}
  value=total_win_count
/>

<BigValue
  data={filtered_provider_info}
  value=fee_debt
/>

<BigValue
  data={filtered_provider_info}
  value=provider_collateral
/>

<BigValue
  data={filtered_provider_info}
  value=pre_commit_deposits
/>

<BigValue
  data={filtered_provider_info}
  value=locked_funds
/>

<BigValue
  data={filtered_provider_info}
  value=balance
/>

<BigValue
  data={filtered_provider_info}
  value=initial_pledge
/>

<BigValue
  data={filtered_provider_info}
  value=mean_spark_retrieval_success_rate_7d
/>

<BigValue
  data={filtered_provider_info}
  value=stddev_spark_retrieval_success_rate_7d
/>

<BigValue
  data={filtered_provider_info}
  value=capacity_utilization_ratio
/>

<BigValue
  data={filtered_provider_info}
  value=started_providing_power_at
/>

<BigValue
  data={filtered_provider_info}
  value=avg_data_uploaded_tibs_per_day
/>


</Grid>

## Daily Data Onboarding

```sql filtered_provider_metrics
select
  date,
  client_id,
  deals,
  onboarded_data_tibs
from filecoin_deals_metrics
where 1=1
  and provider_id = '${params.provider_id}'
  and date between '${inputs.range.start}' and '${inputs.range.end}'
order by date desc, client_id asc
```

<BarChart
  data={filtered_provider_metrics}
  y=onboarded_data_tibs
  series=client_id
  title="Onboarded Data (TiBs)"
  emptySet=pass
  emptySetText="No Deals"
/>

```sql storage_provider_power
select
  date,
  raw_power_pibs,
  quality_adjusted_power_pibs
from filecoin_storage_providers_power
where 1=1
  and provider_id = '${params.provider_id}'
  and date between '${inputs.range.start}' and '${inputs.range.end}'
```

```sql storage_provider_spark_retrievals
select
  date,
  spark_retrieval_success_rate
from filecoin_storage_providers_spark_retrievals
where 1=1
  and provider_id = '${params.provider_id}'
  and date between '${inputs.range.start}' and '${inputs.range.end}'
```

## Retrievals

<LineChart
  data={storage_provider_spark_retrievals}
  x=date
  y=spark_retrieval_success_rate
  title="Retrieval Success Rate (Spark)"
  emptySet=pass
  emptySetText="No Retrievals"
/>

## Provider Power

<Grid cols=2>

<AreaChart
  data={storage_provider_power}
  x=date
  y=raw_power_pibs
  title="Raw Power (PiBs)"
  emptySet=pass
  emptyMessage="No Power Data"
  connectGroup=power
/>

<AreaChart
  data={storage_provider_power}
  x=date
  y=quality_adjusted_power_pibs
  title="Quality Adjusted Power (PiBs)"
  emptySet=pass
  emptyMessage="No Power Data"
  connectGroup=power
/>

</Grid>

## Funds

```sql spe
select
  date,
  provider_id,
  balance,
  locked_funds,
  collateral
from filecoin_storage_providers_economy
where 1=1
  and provider_id = '${params.provider_id}'
  and date between '${inputs.range.start}' and '${inputs.range.end}'
```

<LineChart
  data={spe}
  x=date
  y={["locked_funds", "collateral"]}
  y2="balance"
  emptySet=pass
  emptyMessage="No Power Data"
/>

## Sector Onboarding

```sql spso
select
  date,
  provider_id,
  daily_sector_onboarding_count,
  daily_new_sector_terminated_raw_power_tibs,
  daily_new_sector_fault_raw_power_tibs,
  daily_new_sector_recover_raw_power_tibs,
  daily_new_sector_expire_raw_power_tibs,
  daily_new_sector_extend_raw_power_tibs,
  daily_new_sector_snap_raw_power_tibs
from filecoin_storage_providers_sector_onboarding
where 1=1
  and provider_id = '${params.provider_id}'
  and date between '${inputs.range.start}' and '${inputs.range.end}'
```

<LineChart
  data={spso}
  x=date
  y={["daily_sector_onboarding_count", "daily_new_sector_terminated_raw_power_tibs", "daily_new_sector_fault_raw_power_tibs", "daily_new_sector_recover_raw_power_tibs", "daily_new_sector_expire_raw_power_tibs", "daily_new_sector_extend_raw_power_tibs", "daily_new_sector_snap_raw_power_tibs"]}
/>

## Provider Interactions with Clients

```sql filtered_client_providers
with provider_clients as (
select
  client_id,
  sum(deals) as deals,
  sum(onboarded_data_tibs) as onboarded_data_tibs,
  count(distinct date) as days_with_deals,
  max(date) as last_deal_at,
  min(date) as first_deal_at
from filecoin_deals_metrics
where 1=1
  and provider_id = '${params.provider_id}'
  and date between '${inputs.range.start}' and '${inputs.range.end}'
group by client_id
)

select
  p.client_id,
  p.deals,
  p.onboarded_data_tibs,
  p.days_with_deals,
  p.first_deal_at,
  p.last_deal_at,
  '/client/' || p.client_id as link,
from provider_clients p
order by onboarded_data_tibs desc
```

<DataTable
  data={filtered_client_providers}
  emptySet=pass
  emptyMessage="No Providers"
  rowShading=true
  rowLines=false
  downloadable=true
  link=link
/>
