---
title: Allocators
---

_A detailed view into Filecoin Allocators._

<BigLink href='https://docs.google.com/spreadsheets/d/1uixeylC3pTeOkKh0L2fGsd7YKuyaA6Hse_fhWrm1BIA'>
  <p style="font-size: 1.3rem; text-align: center; font-family: monospace;">Allocators Google Sheets</p>
</BigLink>

```sql allocators_stats
select
  count(distinct allocator_id) as total_approved_allocators,
  sum(initial_allowance_tibs / 1024) as total_allocators_datacap,
  sum(current_allowance_tibs / 1024) as remaining_datacap_allowance,
  total_allocators_datacap - remaining_datacap_allowance as used_datacap_allowance,
  count(distinct allocator_id) filter (initial_allowance_tibs - current_allowance_tibs > 2) as total_active_allocators,
  count(distinct allocator_id) filter (is_multisig) as total_multisig_allocators,
  count(distinct allocator_id) filter (metapathway_type = 'Market-based') as market_based_allocators,
  count(distinct allocator_id) filter (metapathway_type = 'Automatic') as automatic_allocators,
  count(distinct allocator_id) filter (metapathway_type = 'Manual') as manual_allocators,
  count(distinct allocator_id) filter (metapathway_type = 'Market-based' and initial_allowance_tibs - current_allowance_tibs > 2) as active_market_based_allocators,
  count(distinct allocator_id) filter (metapathway_type = 'Automatic' and initial_allowance_tibs - current_allowance_tibs > 2) as active_automatic_allocators,
  count(distinct allocator_id) filter (metapathway_type = 'Manual' and initial_allowance_tibs - current_allowance_tibs > 2) as active_manual_allocators,
  sum(verified_clients_count) as clients_served
from filecoin_allocators
where 1=1
  and is_active
```

<Grid cols=3>

<BigValue
  data={allocators_stats}
  value=total_allocators_datacap
  fmt="pibs"
/>

<BigValue
  data={allocators_stats}
  value=remaining_datacap_allowance
  fmt="pibs"
/>

<BigValue
  data={allocators_stats}
  value=used_datacap_allowance
  fmt="pibs"
/>

<BigValue
  data={allocators_stats}
  value=total_approved_allocators
/>

<BigValue
  data={allocators_stats}
  value=total_active_allocators
/>

<BigValue
  data={allocators_stats}
  value=clients_served
/>

<BigValue
  data={allocators_stats}
  value=manual_allocators
/>

<BigValue
  data={allocators_stats}
  value=market_based_allocators
/>

<BigValue
  data={allocators_stats}
  value=automatic_allocators
/>

<BigValue
  data={allocators_stats}
  value=active_manual_allocators
/>

<BigValue
  data={allocators_stats}
  value=active_market_based_allocators
/>

<BigValue
  data={allocators_stats}
  value=active_automatic_allocators
/>

</Grid>

```sql datacap_evolution
with base_numbers as (
  select
    datacap_allowance_change_tibs as datacap_change,
    cast(height_at as date) as date,
    *,
  from filecoin_datacap_allocations as da
  inner join filecoin_allocators as a on a.allocator_id = da.allocator_id
  where a.is_active
)

select
  date,
  sum(datacap_change) over (order by date rows between unbounded preceding and current row) as remaining_datacap_tibs
from base_numbers
```

<AreaChart
  data={datacap_evolution}
  x=date
  y=remaining_datacap_tibs
  handleMissing=connect
  emptySet=pass
  title="Allocated Unused Datacap"
  yAxisTitle="Allocated Unused Datacap (TiBs)"
/>

## Client Datacap Allocations

```sql allocations
select
  time_bucket(interval '1 week', cast(height_at as date)) as date,
  n.allocator_organization_name as allocator_organization_name,
  sum(a.allowance_tibs) as allowance_tibs
from filecoin_clients_datacap_allowances as a
left join filecoin_allocators as n on n.allocator_id = a.allocator_id
where 1=1
  and n.is_active
group by 1, 2
order by 1 asc
```

<BarChart
  data={allocations}
  x=date
  y=allowance_tibs
  series=allocator_organization_name
  emptySet=pass
/>

## Allocators' Datacap Allocations

```sql allocators_allowances
select
  time_bucket(interval '1 day', cast(height_at as date)) as date,
  sum(a.allowance_tibs / 1024) as allowance_pibs,
  sum(sum(a.allowance_tibs)) over (order by date rows between unbounded preceding and current row) / 1024 as cumulative_allowance_pibs
from filecoin_clients_datacap_allowances as a
left join filecoin_allocators as n on n.allocator_id = a.allocator_id
where 1=1
  and a.allowance_tibs > 0
  and n.is_active
group by 1
order by 1 asc
```

<LineChart
  data={allocators_allowances}
  x=date
  y=cumulative_allowance_pibs
  y2=allowance_pibs
  y2SeriesType=bar
  emptySet=pass
/>

## Explorer

```sql active_allocators
select
  allocator_id,
  '/allocator/' || allocator_id as link,
  metapathway_type,
  left(concat(allocator_organization_name, ' (', allocator_name, ')'), 60) as allocator,
  initial_allowance_tibs / 1024 as initial_allowance_pibs,
  current_allowance_tibs / 1024 as current_allowance_pibs,
  (initial_allowance_tibs - current_allowance_tibs) / 1024 as used_allowance_pibs,
  used_allowance_pibs / initial_allowance_pibs * 100 as used_allowance_percent,
  verified_clients_count,
  created_at,
  allocator_address
from filecoin_allocators
where 1 = 1
  and is_active
order by verified_clients_count desc
```

<DataTable
  data={active_allocators}
  link=link
  search=true
  rows=20
  rowShading=true
  rowLines=false
  downloadable=true
/>

### Country Distribution

```sql country_distribution
select
  location,
  count(distinct allocator_id) as allocators,
  sum(initial_allowance_tibs) as initial_allowance_tibs,
  sum(current_allowance_tibs) as current_allowance_tibs,
  sum(initial_allowance_tibs) - sum(current_allowance_tibs) as used_allowance_tibs,
  sum("12m_requested"::numeric) as requested_tibs,
from filecoin_allocators
where 1 = 1
  and is_active
group by 1
```

<Grid cols=2>

<BarChart
  data={country_distribution}
  x=location
  y=allocators
  connectGroup=country
  labels=true
  title="Allocators by Country"
/>

<BarChart
  data={country_distribution}
  x=location
  y=current_allowance_tibs
  connectGroup=country
  labels=true
  title="Current Allowance by Country"
/>

<BarChart
  data={country_distribution}
  x=location
  y=requested_tibs
  connectGroup=country
  labels=true
  title="Requested Data by Country"
/>

<BarChart
  data={country_distribution}
  x=location
  y=used_allowance_tibs
  connectGroup=country
  labels=true
  title="Used Allowance by Country"
/>

</Grid>

### Pathway Distribution

```sql pathway_distribution
with base as (
  select
    created_at::date as date,
    metapathway_type,
    count(distinct allocator_id) as allocators,
    sum(initial_allowance_tibs) as initial_allowance_tibs,
  from filecoin_allocators
  where 1 = 1
    and is_active
    and metapathway_type is not null
  group by 1, 2
)

select
  date,
  metapathway_type,
  allocators,
  sum(allocators) over (partition by metapathway_type order by date asc rows between unbounded preceding and current row) as total_allocators,
  sum(initial_allowance_tibs) over (partition by metapathway_type order by date asc rows between unbounded preceding and current row) as total_initial_allowance_tibs,
from base
order by date desc
```

<Grid cols=2>

<BarChart
  data={pathway_distribution}
  x=date
  y=allocators
  series=metapathway_type
  emptySet=pass
  title="New Allocators by Pathway"
/>

<AreaChart
  data={pathway_distribution}
  x=date
  y=total_initial_allowance_tibs
  series=metapathway_type
  emptySet=pass
  title="Total Initial Allowance by Pathway"
/>

</Grid>

## Allocators Growth

The table below shows the top allocators by datacap allowance change in the last week and the week before.

```sql top_allocators
select
  a.allocator_id,
  n.allocator_organization_name as allocator_organization_name,
  coalesce(sum(a.allowance_tibs / 1024) filter (where a.height_at > (select max(height_at) from filecoin_clients_datacap_allowances) - interval '1 week'), 0) as allowance_pibs_last_week,
  coalesce(sum(a.allowance_tibs / 1024) filter (
    where a.height_at between (select max(height_at) from filecoin_clients_datacap_allowances) - interval '2 weeks' and (select max(height_at) from filecoin_clients_datacap_allowances) - interval '1 week'
  ), 0) as allowance_pibs_2_weeks_ago,
  allowance_pibs_last_week - allowance_pibs_2_weeks_ago as allowance_pibs_weekly_change,
  '/allocator/' || a.allocator_id as link
from filecoin_clients_datacap_allowances as a
left join filecoin_allocators as n on n.allocator_id = a.allocator_id
where 1=1
  and n.is_active
group by 1, 2
order by 3 desc
```

<DataTable
  data={top_allocators}
  link=link
/>
