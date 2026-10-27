-- asset.description = Warm storage data sets.

-- asset.depends = model.foc_data_sets

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

select
    data_set_id,
    owner,
    provider_id,
    provider_address,
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
    settlement_end_at,
    source,
    metadata,
    with_ipfs_indexing,
    is_cdn_enabled,
    is_deleted,
    api_updated_at_block,
    api_indexed_block,
    api_observed_at
from model.foc_data_sets
order by billing_started_at
