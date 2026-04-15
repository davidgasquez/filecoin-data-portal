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
    'WithdrawRecorded'
  )
),

account_lockup_events as (
  select
    json_extract_string(args, '$.token') as token,
    json_extract_string(args, '$.owner') as owner,
    cast(json_extract(args, '$.lockupCurrent') as decimal(38,0)) as lockup_current,
    cast(json_extract(args, '$.lockupRate') as decimal(38,0)) as lockup_rate,
    cast(json_extract(args, '$.lockupLastSettledAt') as bigint) as lockup_last_settled_at,
    block_number,
    transaction_hash,
    log_index
  from raw_logs
  where event_name = 'AccountLockupSettled'
),

account_lockup_latest as (
  select
    token,
    owner,
    lockup_current,
    lockup_rate,
    lockup_last_settled_at,
    block_number as lockup_block_number
  from account_lockup_events
  qualify row_number() over (
    partition by token, owner
    order by block_number desc, log_index desc
  ) = 1
),

deposit_events as (
  select
    json_extract_string(args, '$.token') as token,
    json_extract_string(args, '$.to') as owner,
    cast(json_extract(args, '$.amount') as decimal(38,0)) as amount,
    block_number
  from raw_logs
  where event_name = 'DepositRecorded'
),

deposits as (
  select
    token,
    owner,
    count(*) as deposit_count,
    sum(amount) as total_deposited,
    max(block_number) as last_deposit_block_number
  from deposit_events
  group by 1, 2
),

withdraw_events as (
  select
    json_extract_string(args, '$.token') as token,
    json_extract_string(args, '$.from') as owner,
    cast(json_extract(args, '$.amount') as decimal(38,0)) as amount,
    block_number
  from raw_logs
  where event_name = 'WithdrawRecorded'
),

withdrawals as (
  select
    token,
    owner,
    count(*) as withdraw_count,
    sum(amount) as total_withdrawn,
    max(block_number) as last_withdraw_block_number
  from withdraw_events
  group by 1, 2
),

account_keys as (
  select token, owner from account_lockup_events
  union
  select token, owner from deposit_events
  union
  select token, owner from withdraw_events
),

tokens as (
  select
    token,
    pow(10, decimals) as scale_factor
  from {{ ref('foc_pay_tokens') }}
)

select
  ak.token,
  ak.owner,
  coalesce(al.lockup_current, cast(0 as decimal(38,0)))
    / coalesce(t.scale_factor, pow(10, 18)) as lockup_current,
  coalesce(al.lockup_rate, cast(0 as decimal(38,0)))
    / coalesce(t.scale_factor, pow(10, 18)) as lockup_rate,
  coalesce(al.lockup_last_settled_at, 0) as lockup_last_settled_at,
  coalesce(dep.deposit_count, 0) as deposit_count,
  coalesce(dep.total_deposited, cast(0 as decimal(38,0)))
    / coalesce(t.scale_factor, pow(10, 18)) as total_deposited,
  coalesce(wd.withdraw_count, 0) as withdraw_count,
  coalesce(wd.total_withdrawn, cast(0 as decimal(38,0)))
    / coalesce(t.scale_factor, pow(10, 18)) as total_withdrawn,
  greatest(
    coalesce(al.lockup_block_number, -1),
    coalesce(dep.last_deposit_block_number, -1),
    coalesce(wd.last_withdraw_block_number, -1)
  ) as last_activity_block_number
from account_keys ak
left join account_lockup_latest al on ak.token = al.token and ak.owner = al.owner
left join deposits dep on ak.token = dep.token and ak.owner = dep.owner
left join withdrawals wd on ak.token = wd.token and ak.owner = wd.owner
left join tokens t on ak.token = t.token
