with
raw_logs as (
  select *
  from {{ source('raw_assets', 'raw_ribrpc_eth_logs_decoded') }}
  where event_name in (
    'RailCreated',
    'RailTerminated'
  )
),
rails_created as (
  select
    cast(json_extract(args, '$.railId') as bigint) as rail_id,
    json_extract_string(args, '$.payer') as payer,
    json_extract_string(args, '$.payee') as payee,
    json_extract_string(args, '$.token') as token,
    json_extract_string(args, '$.operator') as operator,
    json_extract_string(args, '$.validator') as validator,
    json_extract_string(args, '$.serviceFeeRecipient') as service_fee_recipient,
    cast(json_extract(args, '$.commissionRateBps') as bigint) as commission_rate_bps,
    block_number as created_height
  from raw_logs
  where event_name = 'RailCreated'
),
rails_terminated as (
  select
    cast(json_extract(args, '$.railId') as bigint) as rail_id,
    min(block_number) as terminated_height
  from raw_logs
  where event_name = 'RailTerminated'
  group by 1
)
select
  rc.rail_id,
  rc.payer,
  rc.payee,
  rc.token,
  rc.operator,
  rc.validator,
  rc.service_fee_recipient,
  rc.commission_rate_bps,
  rc.created_height,
  to_timestamp(rc.created_height * 30 + 1598306400) as created_at,
  rt.terminated_height,
  to_timestamp(rt.terminated_height * 30 + 1598306400) as terminated_at,
  case
    when rt.terminated_height is null then 'active'
    else 'terminated'
  end as status
from rails_created rc
left join rails_terminated rt on rc.rail_id = rt.rail_id
