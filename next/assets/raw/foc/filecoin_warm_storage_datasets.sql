-- asset.description = Mainnet Filecoin Warm Storage Service datasets created onchain. Includes dataset parties, payment rail identifiers, and billing lifecycle derived from FWSS events.
-- asset.depends = raw.fevm_eth_logs_decoded
-- asset.column = data_set_id | FWSS data set identifier.
-- asset.column = payer | Payer address funding the dataset on mainnet.
-- asset.column = provider_id | Service provider registry identifier selected for the dataset.
-- asset.column = service_provider | Service provider address recorded by FWSS.
-- asset.column = payee | Payee address recorded by FWSS for the dataset.
-- asset.column = pdp_rail_id | Filecoin Pay PDP rail identifier for the dataset.
-- asset.column = cache_miss_rail_id | Filecoin Pay cache-miss rail identifier for the dataset, if CDN is enabled.
-- asset.column = cdn_rail_id | Filecoin Pay CDN rail identifier for the dataset, if CDN is enabled.
-- asset.column = has_cdn | Whether the dataset was created with CDN payment rails.
-- asset.column = created_block | Block when the dataset was created in FWSS.
-- asset.column = created_date | UTC date of dataset creation derived from the creation block.
-- asset.column = billing_started_block | First block where FWSS emitted a positive RailRateUpdated for the dataset.
-- asset.column = billing_started_date | UTC date when the dataset first became chargeable.
-- asset.column = billing_terminated_block | Block where FWSS emitted PDPPaymentTerminated for the dataset, if any.
-- asset.column = billing_terminated_date | UTC date when the PDP billing rail was terminated, if any.
-- asset.column = settlement_end_epoch | Final settlement epoch emitted with PDPPaymentTerminated, if any.
-- asset.column = settlement_end_date | UTC date derived from settlement_end_epoch, if any.
-- asset.not_null = data_set_id
-- asset.not_null = payer
-- asset.not_null = provider_id
-- asset.not_null = service_provider
-- asset.not_null = payee
-- asset.not_null = pdp_rail_id
-- asset.not_null = has_cdn
-- asset.not_null = created_block
-- asset.not_null = created_date
-- asset.unique = data_set_id

with params as (
    select 1598306400 as genesis_timestamp
),
dataset_created as (
    select
        cast(json_extract_string(args, '$.dataSetId') as bigint) as data_set_id,
        lower(json_extract_string(args, '$.payer')) as payer,
        cast(json_extract_string(args, '$.providerId') as bigint) as provider_id,
        lower(json_extract_string(args, '$.serviceProvider')) as service_provider,
        lower(json_extract_string(args, '$.payee')) as payee,
        cast(json_extract_string(args, '$.pdpRailId') as bigint) as pdp_rail_id,
        nullif(cast(json_extract_string(args, '$.cacheMissRailId') as bigint), 0) as cache_miss_rail_id,
        nullif(cast(json_extract_string(args, '$.cdnRailId') as bigint), 0) as cdn_rail_id,
        block_number as created_block,
        date(to_timestamp(block_number * 30 + (select genesis_timestamp from params))) as created_date
    from raw.fevm_eth_logs_decoded
    where abi_name = 'filecoin_warm_storage_service'
      and event_name = 'DataSetCreated'
),
dataset_billing_started as (
    select
        cast(json_extract_string(args, '$.dataSetId') as bigint) as data_set_id,
        min(block_number) as billing_started_block
    from raw.fevm_eth_logs_decoded
    where abi_name = 'filecoin_warm_storage_service'
      and event_name = 'RailRateUpdated'
      and cast(json_extract_string(args, '$.newRate') as bigint) > 0
    group by 1
),
dataset_billing_terminated as (
    select
        data_set_id,
        billing_terminated_block,
        settlement_end_epoch
    from (
        select
            cast(json_extract_string(args, '$.dataSetId') as bigint) as data_set_id,
            block_number as billing_terminated_block,
            cast(json_extract_string(args, '$.endEpoch') as bigint) as settlement_end_epoch,
            row_number() over (
                partition by cast(json_extract_string(args, '$.dataSetId') as bigint)
                order by block_number
            ) as row_num
        from raw.fevm_eth_logs_decoded
        where abi_name = 'filecoin_warm_storage_service'
          and event_name = 'PDPPaymentTerminated'
    )
    where row_num = 1
)
select
    created.data_set_id,
    created.payer,
    created.provider_id,
    created.service_provider,
    created.payee,
    created.pdp_rail_id,
    created.cache_miss_rail_id,
    created.cdn_rail_id,
    created.cache_miss_rail_id is not null or created.cdn_rail_id is not null as has_cdn,
    created.created_block,
    created.created_date,
    started.billing_started_block,
    case
        when started.billing_started_block is null then null
        else date(to_timestamp(started.billing_started_block * 30 + (select genesis_timestamp from params)))
    end as billing_started_date,
    terminated.billing_terminated_block,
    case
        when terminated.billing_terminated_block is null then null
        else date(to_timestamp(terminated.billing_terminated_block * 30 + (select genesis_timestamp from params)))
    end as billing_terminated_date,
    terminated.settlement_end_epoch,
    case
        when terminated.settlement_end_epoch is null then null
        else date(to_timestamp(terminated.settlement_end_epoch * 30 + (select genesis_timestamp from params)))
    end as settlement_end_date
from dataset_created as created
left join dataset_billing_started as started using (data_set_id)
left join dataset_billing_terminated as terminated using (data_set_id)
order by created.created_block, created.data_set_id
