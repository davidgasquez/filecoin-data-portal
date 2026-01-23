with
rails as (
  select *
  from {{ ref('foc_pay_rails') }}
),
rollup as (
  select
    rails.payer,
    min(rails.created_height) as first_rail_created_height,
    max(rails.created_height) as last_rail_created_height,
    sum(case when rails.status = 'active' then 1 else 0 end) as active_rail_count,
    count(*) as total_rail_count,
    sum(case when rails.status = 'terminated' then 1 else 0 end) as terminated_rail_count,
    max(greatest(rails.created_height, coalesce(rails.terminated_height, rails.created_height))) as last_event_height
  from rails
  group by 1
)
select
  payer,
  first_rail_created_height,
  to_timestamp(first_rail_created_height * 30 + 1598306400) as first_rail_created_at,
  last_rail_created_height,
  to_timestamp(last_rail_created_height * 30 + 1598306400) as last_rail_created_at,
  active_rail_count,
  total_rail_count,
  terminated_rail_count,
  case
    when active_rail_count > 0 then 'active'
    else 'inactive'
  end as status,
  last_event_height,
  to_timestamp(last_event_height * 30 + 1598306400) as last_event_at
from rollup
