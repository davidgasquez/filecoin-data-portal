-- asset.description = Warm storage datasets created onchain.

-- asset.depends = raw.fevm_eth_logs_decoded

-- asset.column = dataset_id | FWSS dataset identifier.
-- asset.column = payer | Payer address.
-- asset.column = provider_id | Service provider registry identifier.
-- asset.column = service_provider | Service provider address.
-- asset.column = payee | Payee address.
-- asset.column = pdp_rail_id | Filecoin Pay PDP rail identifier.
-- asset.column = cache_miss_rail_id | Filecoin Pay cache-miss rail identifier, if any.
-- asset.column = cdn_rail_id | Filecoin Pay CDN rail identifier, if any.
-- asset.column = has_cdn | Whether CDN payment rails were configured.
-- asset.column = created_block | Creation block number.
-- asset.column = created_at | UTC creation timestamp.
-- asset.column = billing_started_block | First block with a positive billing rate, if any.
-- asset.column = billing_started_at | UTC billing start timestamp, if any.
-- asset.column = billing_terminated_block | Billing termination block, if any.
-- asset.column = billing_terminated_at | UTC billing termination timestamp, if any.
-- asset.column = settlement_end_epoch | Settlement end epoch, if any.
-- asset.column = settlement_end_at | UTC settlement end timestamp, if any.

-- asset.not_null = dataset_id
-- asset.unique = dataset_id

with params as (
    select 1598306400 as genesis_timestamp
),
dataset_created as (
    select
        cast(json_extract_string(args, '$.dataSetId') as bigint) as dataset_id,
        lower(json_extract_string(args, '$.payer')) as payer,
        cast(json_extract_string(args, '$.providerId') as bigint) as provider_id,
        lower(json_extract_string(args, '$.serviceProvider')) as service_provider,
        lower(json_extract_string(args, '$.payee')) as payee,
        cast(json_extract_string(args, '$.pdpRailId') as bigint) as pdp_rail_id,
        nullif(cast(json_extract_string(args, '$.cacheMissRailId') as bigint), 0) as cache_miss_rail_id,
        nullif(cast(json_extract_string(args, '$.cdnRailId') as bigint), 0) as cdn_rail_id,
        block_number as created_block,
        to_timestamp(block_number * 30 + (select genesis_timestamp from params)) as created_at,
        row_number() over (
            partition by cast(json_extract_string(args, '$.dataSetId') as bigint)
            order by block_number, log_index
        ) as row_num
    from raw.fevm_eth_logs_decoded
    where abi_name = 'filecoin_warm_storage_service'
      and event_name = 'DataSetCreated'
),
dataset_billing_started as (
    select
        cast(json_extract_string(args, '$.dataSetId') as bigint) as dataset_id,
        min(block_number) as billing_started_block
    from raw.fevm_eth_logs_decoded
    where abi_name = 'filecoin_warm_storage_service'
      and event_name = 'RailRateUpdated'
      and cast(json_extract_string(args, '$.newRate') as bigint) > 0
    group by 1
),
dataset_billing_terminated as (
    select
        dataset_id,
        billing_terminated_block,
        settlement_end_epoch
    from (
        select
            cast(json_extract_string(args, '$.dataSetId') as bigint) as dataset_id,
            block_number as billing_terminated_block,
            cast(json_extract_string(args, '$.endEpoch') as bigint) as settlement_end_epoch,
            row_number() over (
                partition by cast(json_extract_string(args, '$.dataSetId') as bigint)
                order by block_number, log_index
            ) as row_num
        from raw.fevm_eth_logs_decoded
        where abi_name = 'filecoin_warm_storage_service'
          and event_name = 'PDPPaymentTerminated'
    )
    where row_num = 1
)
select
    created.dataset_id,
    created.payer,
    created.provider_id,
    created.service_provider,
    created.payee,
    created.pdp_rail_id,
    created.cache_miss_rail_id,
    created.cdn_rail_id,
    created.cache_miss_rail_id is not null or created.cdn_rail_id is not null as has_cdn,
    created.created_block,
    created.created_at,
    started.billing_started_block,
    case
        when started.billing_started_block is null then null
        else to_timestamp(started.billing_started_block * 30 + (select genesis_timestamp from params))
    end as billing_started_at,
    terminated.billing_terminated_block,
    case
        when terminated.billing_terminated_block is null then null
        else to_timestamp(terminated.billing_terminated_block * 30 + (select genesis_timestamp from params))
    end as billing_terminated_at,
    terminated.settlement_end_epoch,
    case
        when terminated.settlement_end_epoch is null then null
        else to_timestamp(terminated.settlement_end_epoch * 30 + (select genesis_timestamp from params))
    end as settlement_end_at
from dataset_created as created
left join dataset_billing_started as started using (dataset_id)
left join dataset_billing_terminated as terminated using (dataset_id)
where created.row_num = 1
