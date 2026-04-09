with
raw_logs as (
  select
    block_number,
    transaction_hash,
    log_index,
    event_name,
    args
  from {{ source('raw_assets', 'raw_ribrpc_eth_logs_decoded') }}
  where event_name in (
    'AccountLockupSettled',
    'DepositRecorded',
    'WithdrawRecorded',
    'OperatorApprovalUpdated',
    'RailCreated',
    'RailTerminated',
    'RailSettled',
    'RailOneTimePaymentProcessed'
  )
),

date_calendar as (
  select
    cast(range as date) as date
  from range(date '2025-10-01', current_date(), interval '1 day')
),

tokens as (
  select
    token,
    pow(10, decimals) as scale_factor
  from {{ ref('foc_pay_tokens') }}
),

account_lockup_events as (
  select
    json_extract_string(args, '$.token') as token,
    json_extract_string(args, '$.owner') as owner,
    cast(json_extract(args, '$.lockupCurrent') as decimal(38,0)) as lockup_current,
    block_number,
    log_index,
    cast(date_trunc('day', to_timestamp(block_number * 30 + 1598306400)) as date) as event_day
  from raw_logs
  where event_name = 'AccountLockupSettled'
),

account_lockup_daily as (
  select
    token,
    owner,
    event_day,
    lockup_current,
    row_number() over (
      partition by token, owner, event_day
      order by block_number desc, log_index desc
    ) as row_num
  from account_lockup_events
  qualify row_num = 1
),

account_lockup_ranges as (
  select
    token,
    owner,
    lockup_current,
    event_day as start_day,
    lead(event_day, 1, current_date() + interval 1 day) over (
      partition by token, owner
      order by event_day
    ) as next_day
  from account_lockup_daily
),

account_lockup_by_day as (
  select
    dc.date,
    al.token,
    al.owner,
    al.lockup_current / coalesce(t.scale_factor, pow(10, 18)) as lockup_current
  from date_calendar dc
  join account_lockup_ranges al
    on dc.date >= al.start_day and dc.date < al.next_day
  left join tokens t on al.token = t.token
),

payer_lockup_by_day as (
  select
    date,
    owner as payer,
    sum(lockup_current) as lockup_current
  from account_lockup_by_day
  group by 1, 2
),

rails_created as (
  select
    cast(json_extract(args, '$.railId') as bigint) as rail_id,
    json_extract_string(args, '$.payer') as payer,
    json_extract_string(args, '$.operator') as operator,
    json_extract_string(args, '$.token') as token,
    cast(date_trunc('day', to_timestamp(block_number * 30 + 1598306400)) as date) as created_day
  from raw_logs
  where event_name = 'RailCreated'
),

rails_terminated as (
  select
    cast(json_extract(args, '$.railId') as bigint) as rail_id,
    cast(date_trunc('day', to_timestamp(block_number * 30 + 1598306400)) as date) as terminated_day
  from raw_logs
  where event_name = 'RailTerminated'
  qualify row_number() over (
    partition by cast(json_extract(args, '$.railId') as bigint)
    order by block_number asc, log_index asc
  ) = 1
),

rails as (
  select
    rc.rail_id,
    rc.payer,
    rc.operator,
    rc.token,
    rc.created_day,
    rt.terminated_day
  from rails_created rc
  left join rails_terminated rt on rc.rail_id = rt.rail_id
),

active_rails as (
  select
    dc.date,
    r.rail_id,
    r.payer,
    r.operator
  from date_calendar dc
  join rails r
    on r.created_day <= dc.date
    and (r.terminated_day is null or r.terminated_day > dc.date)
),

active_rails_by_day as (
  select
    date,
    payer,
    count(*) as active_rail_count
  from active_rails
  group by 1, 2
),

active_payers as (
  select
    ar.date,
    count(distinct ar.payer) as active_payers
  from active_rails_by_day ar
  left join payer_lockup_by_day pl
    on ar.date = pl.date and ar.payer = pl.payer
  where coalesce(pl.lockup_current, 0) > 0
  group by 1
),

active_rails_daily as (
  select
    date,
    count(*) as active_rails
  from active_rails
  group by 1
),

active_operators_daily as (
  select
    date,
    count(distinct operator) as active_operators
  from active_rails
  group by 1
),

locked_tokens as (
  select
    date,
    sum(lockup_current) as locked_tokens
  from account_lockup_by_day
  group by 1
),

settled_events as (
  select
    cast(json_extract(args, '$.railId') as bigint) as rail_id,
    cast(json_extract(args, '$.totalSettledAmount') as decimal(38,0)) as total_settled_amount,
    cast(date_trunc('day', to_timestamp(block_number * 30 + 1598306400)) as date) as event_day
  from raw_logs
  where event_name = 'RailSettled'
),

settled_daily as (
  select
    se.event_day as date,
    sum(se.total_settled_amount / coalesce(t.scale_factor, pow(10, 18))) as settled_amount
  from settled_events se
  left join rails_created rc on se.rail_id = rc.rail_id
  left join tokens t on rc.token = t.token
  group by 1
),

one_time_events as (
  select
    cast(json_extract(args, '$.railId') as bigint) as rail_id,
    cast(json_extract(args, '$.netPayeeAmount') as decimal(38,0)) as net_payee_amount,
    cast(date_trunc('day', to_timestamp(block_number * 30 + 1598306400)) as date) as event_day
  from raw_logs
  where event_name = 'RailOneTimePaymentProcessed'
),

one_time_daily as (
  select
    ote.event_day as date,
    sum(ote.net_payee_amount / coalesce(t.scale_factor, pow(10, 18))) as one_time_net_payee_amount
  from one_time_events ote
  left join rails_created rc on ote.rail_id = rc.rail_id
  left join tokens t on rc.token = t.token
  group by 1
),

deposit_events as (
  select
    json_extract_string(args, '$.token') as token,
    cast(json_extract(args, '$.amount') as decimal(38,0)) as amount,
    cast(date_trunc('day', to_timestamp(block_number * 30 + 1598306400)) as date) as event_day
  from raw_logs
  where event_name = 'DepositRecorded'
),

deposits_daily as (
  select
    de.event_day as date,
    count(*) as deposit_count,
    sum(de.amount / coalesce(t.scale_factor, pow(10, 18))) as deposit_amount
  from deposit_events de
  left join tokens t on de.token = t.token
  group by 1
),

withdraw_events as (
  select
    json_extract_string(args, '$.token') as token,
    cast(json_extract(args, '$.amount') as decimal(38,0)) as amount,
    cast(date_trunc('day', to_timestamp(block_number * 30 + 1598306400)) as date) as event_day
  from raw_logs
  where event_name = 'WithdrawRecorded'
),

withdrawals_daily as (
  select
    we.event_day as date,
    count(*) as withdrawal_count,
    sum(we.amount / coalesce(t.scale_factor, pow(10, 18))) as withdrawal_amount
  from withdraw_events we
  left join tokens t on we.token = t.token
  group by 1
),

operator_approval_events as (
  select
    json_extract_string(args, '$.operator') as operator,
    cast(date_trunc('day', to_timestamp(block_number * 30 + 1598306400)) as date) as event_day
  from raw_logs
  where event_name = 'OperatorApprovalUpdated'
),

operator_approvals_daily as (
  select
    event_day as date,
    count(*) as operator_approval_count
  from operator_approval_events
  group by 1
),

new_rails_daily as (
  select
    created_day as date,
    count(*) as new_rails
  from rails_created
  group by 1
),

terminated_rails_daily as (
  select
    terminated_day as date,
    count(*) as terminated_rails
  from rails_terminated
  group by 1
),

settlement_events_daily as (
  select
    event_day as date,
    count(*) as settlement_event_count
  from settled_events
  group by 1
),

payer_rail_counts as (
  select
    payer,
    count(*) as rail_count,
    count(terminated_day) as terminated_count,
    max(terminated_day) as last_terminated_day
  from rails
  group by 1
),

churned_wallets as (
  select
    last_terminated_day as date,
    count(*) as churned_wallets
  from payer_rail_counts
  where rail_count > 0 and terminated_count = rail_count
  group by 1
),

unique_payers as (
  select
    first_rail_day as date,
    count(*) as unique_payers
  from (
    select
      payer,
      min(created_day) as first_rail_day
    from rails_created
    group by 1
  )
  group by 1
)

select
  dc.date,
  coalesce(ap.active_payers, 0) as active_payers,
  coalesce(ar.active_rails, 0) as active_rails,
  coalesce(nr.new_rails, 0) as new_rails,
  coalesce(tr.terminated_rails, 0) as terminated_rails,
  coalesce(ao.active_operators, 0) as active_operators,
  coalesce(oa.operator_approval_count, 0) as operator_approval_count,
  coalesce(lt.locked_tokens, 0) as locked_tokens,
  coalesce(sd.settled_amount, 0) as settled_amount,
  coalesce(se.settlement_event_count, 0) as settlement_event_count,
  coalesce(ot.one_time_net_payee_amount, 0) as one_time_net_payee_amount,
  coalesce(dd.deposit_count, 0) as deposit_count,
  coalesce(dd.deposit_amount, 0) as deposit_amount,
  coalesce(wd.withdrawal_count, 0) as withdrawal_count,
  coalesce(wd.withdrawal_amount, 0) as withdrawal_amount,
  coalesce(cw.churned_wallets, 0) as churned_wallets,
  coalesce(up.unique_payers, 0) as unique_payers
from date_calendar dc
left join active_payers ap on dc.date = ap.date
left join active_rails_daily ar on dc.date = ar.date
left join new_rails_daily nr on dc.date = nr.date
left join terminated_rails_daily tr on dc.date = tr.date
left join active_operators_daily ao on dc.date = ao.date
left join operator_approvals_daily oa on dc.date = oa.date
left join locked_tokens lt on dc.date = lt.date
left join settled_daily sd on dc.date = sd.date
left join settlement_events_daily se on dc.date = se.date
left join one_time_daily ot on dc.date = ot.date
left join deposits_daily dd on dc.date = dd.date
left join withdrawals_daily wd on dc.date = wd.date
left join churned_wallets cw on dc.date = cw.date
left join unique_payers up on dc.date = up.date
order by dc.date
