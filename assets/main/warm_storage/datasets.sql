-- asset.description = Warm storage datasets.

-- asset.depends = model.warm_storage_datasets

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

select
    dataset_id,
    payer,
    provider_id,
    service_provider,
    payee,
    pdp_rail_id,
    cache_miss_rail_id,
    cdn_rail_id,
    has_cdn,
    created_block,
    created_at,
    billing_started_block,
    billing_started_at,
    billing_terminated_block,
    billing_terminated_at,
    settlement_end_epoch,
    settlement_end_at
from model.warm_storage_datasets
order by billing_started_at
