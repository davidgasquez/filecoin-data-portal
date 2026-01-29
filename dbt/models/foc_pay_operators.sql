with
operator_approvals as (
  select
    json_extract_string(args, '$.operator') as operator,
    block_number
  from {{ source('raw_assets', 'raw_ribrpc_eth_logs_decoded') }}
  where event_name = 'OperatorApprovalUpdated'
),

approval_stats as (
  select
    operator,
    count(*) as approval_count,
    max(block_number) as last_approval_block_number
  from operator_approvals
  group by 1
),

rail_stats as (
  select
    operator,
    count(*) as rail_count,
    sum(total_commission_amount) as total_commission_amount,
    max(last_activity_block_number) as last_rail_activity_block_number
  from {{ ref('foc_pay_rails') }}
  group by 1
),

operator_keys as (
  select operator from operator_approvals
  union
  select operator from {{ ref('foc_pay_rails') }}
)

select
  ok.operator,
  coalesce(rs.rail_count, 0) as rail_count,
  coalesce(ap.approval_count, 0) as approval_count,
  coalesce(rs.total_commission_amount, cast(0 as decimal(38,0))) as total_commission_amount,
  greatest(
    coalesce(rs.last_rail_activity_block_number, -1),
    coalesce(ap.last_approval_block_number, -1)
  ) as last_activity_block_number
from operator_keys ok
left join rail_stats rs on ok.operator = rs.operator
left join approval_stats ap on ok.operator = ap.operator
