# {$page.params.allocator_id}

```sql filtered_allocator_info
select
  *,
  cast(cast(application_number as int) as string) as issue_number,
from filecoin_allocators
where allocator_id = '${params.allocator_id}'
```

<Grid cols=2>

<BigLink href='{fmt(filtered_allocator_info[0].application_url)}'>
  Application URL
</BigLink>

<BigLink href='https://github.com/filecoin-project/notary-governance/issues/{fmt(filtered_allocator_info[0].issue_number)}'>
  Application Issue
</BigLink>

</Grid>

<Grid cols=4>

<BigValue
  data={filtered_allocator_info}
  value=allocator_name
  title="Name"
/>

<BigValue
  data={filtered_allocator_info}
  value=allocator_organization_name
  title="Organization"
/>

<BigValue
  data={filtered_allocator_info}
  value=is_multisig
  title="Is Multisig?"
/>

<BigValue
  data={filtered_allocator_info}
  value=allocator_address
  title="Address"
/>

<BigValue
  data={filtered_allocator_info}
  value=allocator_eth_address
  title="ETH Address"
/>

<BigValue
  data={filtered_allocator_info}
  value=initial_allowance_tibs
  title="Initial Allowance (TiBs)"
/>

<BigValue
  data={filtered_allocator_info}
  value=current_allowance_tibs
  title="Current Allowance (TiBs)"
/>

<BigValue
  data={filtered_allocator_info}
  value=remaining_datacap_tibs
  title="Reported Remaining (TiBs)"
/>

<BigValue
  data={filtered_allocator_info}
  value=created_at
  title="Created At"
/>

<BigValue
  data={filtered_allocator_info}
  value=verified_clients_count
  title="Verified Clients"
/>

<BigValue
  data={filtered_allocator_info}
  value=received_datacap_change_tibs
  title="Received Datacap Change (TiBs)"
/>

<BigValue
  data={filtered_allocator_info}
  value=received_datacap_change_90d_tibs
  title="Received Change 90d (TiBs)"
/>

<BigValue
  data={filtered_allocator_info}
  value=datacap_source
  title="Datacap Source"
/>

<BigValue
  data={filtered_allocator_info}
  value=audit_status
  title="Audit Status"
/>

<BigValue
  data={filtered_allocator_info}
  value=is_virtual
  title="Virtual?"
/>

<BigValue
  data={filtered_allocator_info}
  value=is_meta_allocator
  title="Meta Allocator?"
/>

<BigValue
  data={filtered_allocator_info}
  value=message_created_at
  title="Message Created At"
/>

<BigValue
  data={filtered_allocator_info}
  value=metapathway_type
/>

<BigValue
  data={filtered_allocator_info}
  value=associated_org_addresses
/>

<BigValue
  data={filtered_allocator_info}
  value=is_standardized
/>

<BigValue
  data={filtered_allocator_info}
  value=number_of_target_clients
/>

<BigValue
  data={filtered_allocator_info}
  value=minimum_required_storage_provider_replication
/>

<BigValue
  data={filtered_allocator_info}
  value=minimum_required_replicas
/>

<BigValue
  data={filtered_allocator_info}
  value=tooling
/>

<BigValue
  data={filtered_allocator_info}
  value=12m_requested
/>

<BigValue
  data={filtered_allocator_info}
  value=github_handle
/>

<BigValue
  data={filtered_allocator_info}
  value=pathway_addresses_msig
/>

</Grid>

```sql datacap_balance_history
select
  height_at::date as date,
  mean(remaining_datacap_tibs) as datacap
from filecoin_datacap_allocations
where allocator_id = '${params.allocator_id}'
group by date
order by date desc
```

## Datacap Changes

<AreaChart
  data={datacap_balance_history}
  x=date
  y=datacap
  step=true
  handleMissing=connect
  emptySet=pass
/>

## Client Datacap Allocations

```sql datacap_allowances
select
  cda.audit_trail,
  cda.client_id,
  clients.client_name,
  cda.allowance_tibs,
  cda.height_at,
  cda.dc_source,
  cda.issue_created_at,
  cda.messaged_created_at,
  cda.has_remaining_allowance,
  cda.allocation_request_type,
  cda.message_cid,
  split_part(split_part(audit_trail, '/', -1), '/', 1) as allowance_number,
  concat('#', allowance_number, ' by ', allocation_request_github_username) as allowance_label,
  concat('https://filfox.info/en/message/', message_cid) as message_cid_link,
from filecoin_clients_datacap_allowances as cda
left join filecoin_clients as clients on clients.client_id = cda.client_id
where 1=1
  and cda.allocator_id = '${params.allocator_id}'
  and cda.audit_trail is not null
order by height_at desc
```

<DataTable
  data={datacap_allowances}
  emptySet=pass
  rowShading=true
>
  <Column id=audit_trail contentType=link linkLabel=allowance_label title="Allowance"/>
  <Column id=client_id title="Client"/>
  <Column id=client_name/>
  <Column id=allowance_tibs/>
  <Column id=height_at title="Timestamp"/>
  <Column id=dc_source title="Source"/>
  <Column id=issue_created_at title="Issue Created"/>
  <Column id=messaged_created_at title="Message Created"/>
  <Column id=has_remaining_allowance title="Remaining?"/>
  <Column id=allocation_request_type/>
  <Column id=message_cid_link contentType=link linkLabel=message_cid title="Message"/>
</DataTable>

### Client Details

```sql allowances_client_details
select
  client_id,
  client_name,
  region,
  total_active_deals,
  total_data_uploaded_tibs,
  unique_data_uploaded_tibs as total_unique_data_uploaded,
  first_deal_at,
  last_deal_at,
  total_active_unique_providers as providers_with_deals,
  current_datacap_tibs,
from filecoin_clients
where client_id in (select client_id from (select * from filecoin_clients_datacap_allowances where allocator_id = '${params.allocator_id}'))
```

<DataTable
  data={allowances_client_details}
  emptySet=pass
  emptyMessage="No Clients"
/>

```sql client_data_onboarding
select
  date,
  client_id,
  sum(deals) as deals,
  sum(onboarded_data_tibs) as onboarded_data_tibs,
from filecoin_deals_metrics
where client_id in (select client_id from (select *from filecoin_clients_datacap_allowances where allocator_id = '${params.allocator_id}'))
group by 1, 2
order by 1 desc
```

<BarChart
  data={client_data_onboarding}
  x=date
  y=onboarded_data_tibs
  series=client_id
  emptySet=pass
  yFmt="pibs"
  title="Data Onboarding by Allocator's Client"
/>
