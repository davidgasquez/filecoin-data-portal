-- asset.description = Filecoin Pay rails reconstructed from onchain events.

-- asset.depends = raw.fevm_eth_logs_decoded

-- asset.column = rail_id | Filecoin Pay rail identifier.
-- asset.column = payer | Payer address.
-- asset.column = payee | Payee address.
-- asset.column = token | ERC20 token address.
-- asset.column = operator | Operator address.
-- asset.column = service | Service classification.
-- asset.column = validator | Validator address.
-- asset.column = service_fee_recipient | Service fee recipient address.
-- asset.column = commission_rate_bps | Commission rate in basis points.
-- asset.column = is_arr_eligible | Whether the rail counts toward ARR.
-- asset.column = created_block | Creation block number.
-- asset.column = created_log_index | Creation log index.
-- asset.column = created_transaction_hash | Creation transaction hash.
-- asset.column = created_date | UTC creation date.
-- asset.column = terminated_block | Termination block number, if any.
-- asset.column = terminated_log_index | Termination log index, if any.
-- asset.column = terminated_transaction_hash | Termination transaction hash, if any.
-- asset.column = terminated_by | Address that terminated the rail, if any.
-- asset.column = terminated_end_epoch | End epoch emitted on termination, if any.
-- asset.column = terminated_date | UTC termination date, if any.
-- asset.column = terminated_end_date | UTC termination end date, if any.
-- asset.column = is_terminated | Whether the rail has a termination event.

-- asset.not_null = rail_id
-- asset.unique = rail_id

with params as (
    select
        1598306400 as genesis_timestamp,
        '0x80b98d3aa09ffff255c3ba4a241111ff1262f045' as usdfc_token,
        '0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71' as dealbot_payer,
        '0x56e53c5e7f27504b810494cc3b88b2aa0645a839' as storacha_operator
),
rail_created as (
    select
        cast(json_extract_string(args, '$.railId') as bigint) as rail_id,
        lower(json_extract_string(args, '$.payer')) as payer,
        lower(json_extract_string(args, '$.payee')) as payee,
        lower(json_extract_string(args, '$.token')) as token,
        lower(json_extract_string(args, '$.operator')) as operator,
        lower(json_extract_string(args, '$.validator')) as validator,
        lower(json_extract_string(args, '$.serviceFeeRecipient')) as service_fee_recipient,
        cast(json_extract_string(args, '$.commissionRateBps') as bigint) as commission_rate_bps,
        block_number as created_block,
        log_index as created_log_index,
        transaction_hash as created_transaction_hash,
        date(to_timestamp(block_number * 30 + (select genesis_timestamp from params))) as created_date,
        row_number() over (
            partition by cast(json_extract_string(args, '$.railId') as bigint)
            order by block_number, log_index
        ) as row_num
    from raw.fevm_eth_logs_decoded
    where abi_name = 'filecoin_pay_v1'
      and event_name = 'RailCreated'
),
rail_terminated as (
    select
        cast(json_extract_string(args, '$.railId') as bigint) as rail_id,
        block_number as terminated_block,
        log_index as terminated_log_index,
        transaction_hash as terminated_transaction_hash,
        lower(json_extract_string(args, '$.by')) as terminated_by,
        cast(json_extract_string(args, '$.endEpoch') as bigint) as terminated_end_epoch,
        date(to_timestamp(block_number * 30 + (select genesis_timestamp from params))) as terminated_date,
        date(to_timestamp(cast(json_extract_string(args, '$.endEpoch') as bigint) * 30 + (select genesis_timestamp from params))) as terminated_end_date,
        row_number() over (
            partition by cast(json_extract_string(args, '$.railId') as bigint)
            order by block_number, log_index
        ) as row_num
    from raw.fevm_eth_logs_decoded
    where abi_name = 'filecoin_pay_v1'
      and event_name = 'RailTerminated'
)
select
    created.rail_id,
    created.payer,
    created.payee,
    created.token,
    created.operator,
    case
        when created.operator = (select storacha_operator from params) then 'Storacha'
        else 'FWSS'
    end as service,
    created.validator,
    created.service_fee_recipient,
    created.commission_rate_bps,
    created.token = (select usdfc_token from params)
        and created.payer != (select dealbot_payer from params) as is_arr_eligible,
    created.created_block,
    created.created_log_index,
    created.created_transaction_hash,
    created.created_date,
    terminated.terminated_block,
    terminated.terminated_log_index,
    terminated.terminated_transaction_hash,
    terminated.terminated_by,
    terminated.terminated_end_epoch,
    terminated.terminated_date,
    terminated.terminated_end_date,
    terminated.terminated_block is not null as is_terminated
from rail_created as created
left join rail_terminated as terminated
    on created.rail_id = terminated.rail_id
   and terminated.row_num = 1
where created.row_num = 1
order by created_date desc
