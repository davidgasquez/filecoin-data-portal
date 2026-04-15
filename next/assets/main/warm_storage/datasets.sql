-- asset.description = Published warm storage datasets.

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
-- asset.column = created_date | UTC creation date.
-- asset.column = billing_started_block | First block with a positive billing rate, if any.
-- asset.column = billing_started_date | UTC billing start date, if any.
-- asset.column = billing_terminated_block | Billing termination block, if any.
-- asset.column = billing_terminated_date | UTC billing termination date, if any.
-- asset.column = settlement_end_epoch | Settlement end epoch, if any.
-- asset.column = settlement_end_date | UTC settlement end date, if any.

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
    created_date,
    billing_started_block,
    billing_started_date,
    billing_terminated_block,
    billing_terminated_date,
    settlement_end_epoch,
    settlement_end_date
from model.warm_storage_datasets
