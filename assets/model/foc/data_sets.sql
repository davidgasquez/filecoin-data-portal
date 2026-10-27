-- asset.description = Warm storage data sets created onchain.

-- asset.depends = model.pay_rail_rate_intervals
-- asset.depends = raw.riba_eth_logs_decoded
-- asset.depends = raw.filecoin_api_data_sets

-- asset.column = data_set_id | FWSS data set identifier.
-- asset.column = owner | Client address that pays for the data set.
-- asset.column = provider_id | Service provider registry identifier.
-- asset.column = provider_address | Service provider address.
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
-- asset.column = source | Current source metadata value, from the Filecoin API.
-- asset.column = metadata | Current data set metadata as JSON, from the Filecoin API.
-- asset.column = with_ipfs_indexing | Whether IPFS indexing is requested, from the Filecoin API.
-- asset.column = is_cdn_enabled | Whether CDN is currently enabled, from the Filecoin API.
-- asset.column = is_deleted | Whether the data set is currently deleted, from the Filecoin API.
-- asset.column = api_updated_at_block | Last API indexer update block, not a verified event block.
-- asset.column = api_indexed_block | Latest API indexer block before the snapshot.
-- asset.column = api_observed_at | UTC Filecoin API snapshot timestamp.

-- asset.not_null = data_set_id
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
        to_timestamp(block_number * 30 + (select genesis_timestamp from params)) as created_at,
        row_number() over (
            partition by cast(json_extract_string(args, '$.dataSetId') as bigint)
            order by block_number, log_index
        ) as row_num
    from raw.riba_eth_logs_decoded
    where contract_name = 'filecoin_warm_storage_service'
      and event_name = 'DataSetCreated'
),
dataset_billing_started as (
    select
        created.data_set_id,
        intervals.start_block as billing_started_block,
        intervals.start_at as billing_started_at
    from dataset_created as created
    join model.pay_rail_rate_intervals as intervals
        on created.pdp_rail_id = intervals.rail_id
    where created.row_num = 1
      and intervals.rate_wei_per_epoch > 0
    qualify row_number() over (
        partition by created.data_set_id
        order by intervals.start_ordinal
    ) = 1
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
                order by block_number, log_index
            ) as row_num
        from raw.riba_eth_logs_decoded
        where contract_name = 'filecoin_warm_storage_service'
          and event_name = 'PDPPaymentTerminated'
    )
    where row_num = 1
)
select
    created.data_set_id,
    created.payer as owner,
    created.provider_id,
    created.service_provider as provider_address,
    created.payee,
    created.pdp_rail_id,
    created.cache_miss_rail_id,
    created.cdn_rail_id,
    created.cache_miss_rail_id is not null or created.cdn_rail_id is not null as has_cdn,
    created.created_block,
    created.created_at,
    started.billing_started_block,
    started.billing_started_at,
    terminated.billing_terminated_block,
    case
        when terminated.billing_terminated_block is null then null
        else to_timestamp(terminated.billing_terminated_block * 30 + (select genesis_timestamp from params))
    end as billing_terminated_at,
    terminated.settlement_end_epoch,
    case
        when terminated.settlement_end_epoch is null then null
        else to_timestamp(terminated.settlement_end_epoch * 30 + (select genesis_timestamp from params))
    end as settlement_end_at,
    api.source,
    api.metadata,
    api.with_ipfs_indexing,
    api.with_cdn as is_cdn_enabled,
    api.deleted as is_deleted,
    api.updated_at_block as api_updated_at_block,
    api.indexed_block as api_indexed_block,
    api.observed_at as api_observed_at
from dataset_created as created
left join dataset_billing_started as started using (data_set_id)
left join dataset_billing_terminated as terminated using (data_set_id)
left join raw.filecoin_api_data_sets as api using (data_set_id)
where created.row_num = 1
