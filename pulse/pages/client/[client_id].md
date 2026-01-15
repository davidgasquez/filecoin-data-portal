# {$page.params.client_id}

<DateRange
  name=range
  start=2020-09-01
  defaultValue={'Last 365 Days'}
/>

```sql filtered_client
select
  *
from filecoin_clients
where client_id = '${params.client_id}'
```

<Grid cols=3>

<BigValue
  data={filtered_client}
  value=client_name
  title="Name"
/>

<BigValue
  data={filtered_client}
  value=total_active_deals
  title="Active Deals"
/>

<BigValue
  data={filtered_client}
  value=total_active_data_uploaded_tibs
  title="Active Data (TiBs)"
/>

<BigValue
  data={filtered_client}
  value=first_deal_at
  title="First Deal"
/>

<BigValue
  data={filtered_client}
  value=last_deal_at
  title="Last Deal"
/>


<BigValue
  data={filtered_client}
  value=total_active_unique_providers
  title="Active Providers"
/>

<BigValue
  data={filtered_client}
  value=region
  title="Region"
/>

<BigValue
  data={filtered_client}
  value=current_datacap_tibs
  title="Current Datacap (TiBs)"
/>

<BigValue
  data={filtered_client}
  value=allocator_id
/>


</Grid>

### Datacap Stats

<Grid cols=3>

<BigValue
  data={filtered_client}
  value=verifier_name
  title="Verifier"
/>

<BigValue
  data={filtered_client}
  value=datacap_deal_count
  title="Datacap Deals"
/>

<BigValue
  data={filtered_client}
  value=datacap_provider_count
  title="Datacap Providers"
/>

<BigValue
  data={filtered_client}
  value=top_provider
  title="Top Provider"
/>

<BigValue
  data={filtered_client}
  value=used_datacap_tibs
  title="Used Datacap (TiBs)"
/>

<BigValue
  data={filtered_client}
  value=reported_remaining_datacap_tibs
  title="Reported Remaining (TiBs)"
/>

<BigValue
  data={filtered_client}
  value=received_datacap_change_tibs
  title="Received Change (TiBs)"
/>

<BigValue
  data={filtered_client}
  value=received_datacap_change_90d_tibs
  title="Received Change 90d (TiBs)"
/>

<BigValue
  data={filtered_client}
  value=used_datacap_change_tibs
  title="Used Change (TiBs)"
/>

<BigValue
  data={filtered_client}
  value=used_datacap_change_90d_tibs
  title="Used Change 90d (TiBs)"
/>

<BigValue
  data={filtered_client}
  value=datacap_issue_created_at
  title="Issue Created At"
/>

<BigValue
  data={filtered_client}
  value=datacap_message_created_at
  title="Message Created At"
/>

<BigValue
  data={filtered_client}
  value=datacap_retries
  title="Retries"
/>

</Grid>

```sql filtered_client_metrics
select
  date,
  provider_id,
  deals,
  onboarded_data_tibs
from filecoin_deals_metrics
where 1=1
  and client_id = '${params.client_id}'
  and date between '${inputs.range.start}' and '${inputs.range.end}'
order by date desc, provider_id asc
```

## Daily Data Onboarding

<BarChart
  data={filtered_client_metrics}
  y=onboarded_data_tibs
  series=provider_id
  title="Onboarded Data (TiBs)"
/>

<!-- <CalendarHeatmap
  data={filtered_client_metrics}
  date=date
  value=onboarded_data_tibs
  title="Onboarding Data (TiBs)"
/> -->


## Client Interactions with Storage Providers

```sql filtered_client_providers
with client_provider_metrics as (
select
  provider_id,
  sum(deals) as deals,
  sum(onboarded_data_tibs) as onboarded_data_tibs,
  count(distinct date) as days_with_deals,
  max(date) as last_deal_at,
  min(date) as first_deal_at
from filecoin_deals_metrics
where 1=1
  and client_id = '${params.client_id}'
  and date between '${inputs.range.start}' and '${inputs.range.end}'
group by provider_id
)

select
  p.provider_id,
  p.deals,
  p.onboarded_data_tibs,
  p.days_with_deals,
  deals / sp.total_deals as client_provider_deal_share,
  onboarded_data_tibs / sp.total_data_uploaded_tibs as client_provider_data_share,
  p.first_deal_at,
  p.last_deal_at,
  sp.total_unique_clients,
  sp.raw_power_pibs,
  sp.quality_adjusted_power_pibs,
  sp.provider_name,
  sp.balance,
  sp.locked_funds,
  sp.provider_collateral,
  '/provider/' || p.provider_id as link,
from client_provider_metrics p
left join filecoin_storage_providers sp on p.provider_id = sp.provider_id
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
