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
    'RailCreated',
    'RailLockupModified',
    'RailRateModified',
    'RailSettled',
    'RailOneTimePaymentProcessed',
    'RailTerminated',
    'RailFinalized'
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
    block_number as created_block_number,
    transaction_hash as created_transaction_hash,
    log_index as created_log_index
  from raw_logs
  where event_name = 'RailCreated'
),

rail_lockup_latest as (
  select
    cast(json_extract(args, '$.railId') as bigint) as rail_id,
    cast(json_extract(args, '$.newLockupPeriod') as bigint) as lockup_period,
    cast(json_extract(args, '$.newLockupFixed') as decimal(38,0)) as lockup_fixed,
    block_number as lockup_block_number,
    transaction_hash as lockup_transaction_hash,
    log_index as lockup_log_index
  from raw_logs
  where event_name = 'RailLockupModified'
  qualify row_number() over (
    partition by cast(json_extract(args, '$.railId') as bigint)
    order by block_number desc, log_index desc
  ) = 1
),

rail_rate_latest as (
  select
    cast(json_extract(args, '$.railId') as bigint) as rail_id,
    cast(json_extract(args, '$.newRate') as decimal(38,0)) as payment_rate,
    block_number as rate_block_number,
    transaction_hash as rate_transaction_hash,
    log_index as rate_log_index
  from raw_logs
  where event_name = 'RailRateModified'
  qualify row_number() over (
    partition by cast(json_extract(args, '$.railId') as bigint)
    order by block_number desc, log_index desc
  ) = 1
),

rail_settlement_events as (
  select
    cast(json_extract(args, '$.railId') as bigint) as rail_id,
    cast(json_extract(args, '$.totalSettledAmount') as decimal(38,0)) as total_settled_amount,
    cast(json_extract(args, '$.totalNetPayeeAmount') as decimal(38,0)) as total_net_payee_amount,
    cast(json_extract(args, '$.operatorCommission') as decimal(38,0)) as operator_commission,
    cast(json_extract(args, '$.networkFee') as decimal(38,0)) as network_fee,
    cast(json_extract(args, '$.settledUpTo') as bigint) as settled_up_to,
    block_number
  from raw_logs
  where event_name = 'RailSettled'
),

rail_settlements as (
  select
    rail_id,
    count(*) as settlement_count,
    sum(total_settled_amount) as total_settled_amount,
    sum(total_net_payee_amount) as total_net_payee_amount,
    sum(operator_commission) as settled_commission_amount,
    sum(network_fee) as settled_network_fee,
    max(settled_up_to) as settled_up_to,
    max(block_number) as last_settlement_block_number
  from rail_settlement_events
  group by 1
),

rail_one_time_events as (
  select
    cast(json_extract(args, '$.railId') as bigint) as rail_id,
    cast(json_extract(args, '$.netPayeeAmount') as decimal(38,0)) as net_payee_amount,
    cast(json_extract(args, '$.operatorCommission') as decimal(38,0)) as operator_commission,
    cast(json_extract(args, '$.networkFee') as decimal(38,0)) as network_fee,
    block_number
  from raw_logs
  where event_name = 'RailOneTimePaymentProcessed'
),

rail_one_time_payments as (
  select
    rail_id,
    count(*) as one_time_payment_count,
    sum(net_payee_amount) as total_one_time_net_payee_amount,
    sum(operator_commission) as one_time_commission_amount,
    sum(network_fee) as one_time_network_fee,
    sum(net_payee_amount + operator_commission + network_fee) as total_one_time_gross_amount,
    max(block_number) as last_one_time_payment_block_number
  from rail_one_time_events
  group by 1
),

rail_terminated as (
  select
    cast(json_extract(args, '$.railId') as bigint) as rail_id,
    json_extract_string(args, '$.by') as terminated_by,
    cast(json_extract(args, '$.endEpoch') as bigint) as end_epoch,
    block_number as terminated_block_number,
    transaction_hash as terminated_transaction_hash,
    log_index as terminated_log_index
  from raw_logs
  where event_name = 'RailTerminated'
  qualify row_number() over (
    partition by cast(json_extract(args, '$.railId') as bigint)
    order by block_number asc, log_index asc
  ) = 1
),

rail_finalized as (
  select
    cast(json_extract(args, '$.railId') as bigint) as rail_id,
    block_number as finalized_block_number,
    transaction_hash as finalized_transaction_hash,
    log_index as finalized_log_index
  from raw_logs
  where event_name = 'RailFinalized'
  qualify row_number() over (
    partition by cast(json_extract(args, '$.railId') as bigint)
    order by block_number asc, log_index asc
  ) = 1
),

tokens as (
  select
    token,
    pow(10, decimals) as scale_factor
  from {{ ref('foc_pay_tokens') }}
),

rail_base as (
  select
    rc.rail_id,
    rc.payer,
    rc.payee,
    rc.token,
    rc.operator,
    rc.validator,
    rc.service_fee_recipient,
    rc.commission_rate_bps,
    rl.lockup_period,
    rl.lockup_fixed as lockup_fixed_raw,
    rl.lockup_fixed - coalesce(otp.total_one_time_gross_amount, 0) as lockup_fixed_current_raw,
    rr.payment_rate as payment_rate_raw,
    rs.settled_up_to,
    rt.end_epoch,
    rt.terminated_by,
    rf.finalized_block_number,
    rc.created_block_number,
    rc.created_transaction_hash,
    rc.created_log_index,
    rt.terminated_block_number,
    rt.terminated_transaction_hash,
    rt.terminated_log_index,
    rf.finalized_transaction_hash,
    rf.finalized_log_index,
    rs.settlement_count,
    rs.total_settled_amount as total_settled_amount_raw,
    rs.total_net_payee_amount as total_net_payee_amount_raw,
    coalesce(rs.settled_commission_amount, 0) + coalesce(otp.one_time_commission_amount, 0) as total_commission_amount_raw,
    coalesce(rs.settled_network_fee, 0) + coalesce(otp.one_time_network_fee, 0) as total_network_fee_raw,
    otp.one_time_payment_count,
    otp.total_one_time_net_payee_amount as total_one_time_net_payee_amount_raw,
    greatest(
      rc.created_block_number,
      coalesce(rl.lockup_block_number, -1),
      coalesce(rr.rate_block_number, -1),
      coalesce(rs.last_settlement_block_number, -1),
      coalesce(otp.last_one_time_payment_block_number, -1),
      coalesce(rt.terminated_block_number, -1),
      coalesce(rf.finalized_block_number, -1)
    ) as last_activity_block_number,
    coalesce(t.scale_factor, pow(10, 18)) as scale_factor
  from rails_created rc
  left join rail_lockup_latest rl on rc.rail_id = rl.rail_id
  left join rail_rate_latest rr on rc.rail_id = rr.rail_id
  left join rail_settlements rs on rc.rail_id = rs.rail_id
  left join rail_one_time_payments otp on rc.rail_id = otp.rail_id
  left join rail_terminated rt on rc.rail_id = rt.rail_id
  left join rail_finalized rf on rc.rail_id = rf.rail_id
  left join tokens t on rc.token = t.token
)

select
  rail_id,
  payer,
  payee,
  token,
  operator,
  validator,
  service_fee_recipient,
  commission_rate_bps,
  lockup_period,
  lockup_fixed_raw / scale_factor as lockup_fixed,
  lockup_fixed_current_raw / scale_factor as lockup_fixed_current,
  payment_rate_raw / scale_factor as payment_rate,
  settled_up_to,
  end_epoch,
  terminated_by,
  finalized_block_number,
  created_block_number,
  to_timestamp(created_block_number * 30 + 1598306400) as created_at,
  created_transaction_hash,
  created_log_index,
  terminated_block_number,
  to_timestamp(terminated_block_number * 30 + 1598306400) as terminated_at,
  terminated_transaction_hash,
  terminated_log_index,
  to_timestamp(finalized_block_number * 30 + 1598306400) as finalized_at,
  finalized_transaction_hash,
  finalized_log_index,
  case
    when finalized_block_number is not null then 'finalized'
    when terminated_block_number is not null then 'terminated'
    else 'active'
  end as status,
  settlement_count,
  total_settled_amount_raw / scale_factor as total_settled_amount,
  total_net_payee_amount_raw / scale_factor as total_net_payee_amount,
  total_commission_amount_raw / scale_factor as total_commission_amount,
  total_network_fee_raw / scale_factor as total_network_fee,
  one_time_payment_count,
  total_one_time_net_payee_amount_raw / scale_factor as total_one_time_net_payee_amount,
  last_activity_block_number
from rail_base
