-- asset.description = PDP service providers.

-- asset.depends = model.foc_providers

-- asset.column = provider_id | Service provider registry identifier.
-- asset.column = name | Provider name declared in the registry.
-- asset.column = description | Provider description declared in the registry.
-- asset.column = provider_address | Provider control address.
-- asset.column = payee | Payee address.
-- asset.column = is_registered | Whether the provider has a registration event.
-- asset.column = is_removed | Whether the provider has a removal event.
-- asset.column = removed_block | Removal block number, if any.
-- asset.column = removed_transaction_hash | Removal transaction hash, if any.
-- asset.column = removed_at | UTC removal timestamp, if any.
-- asset.column = is_provider_active | Whether the registry marks the provider active at the snapshot block.
-- asset.column = is_endorsed | Whether the provider is in the endorsement set at the snapshot block.
-- asset.column = product_type | Latest PDP product type label.
-- asset.column = offers_pdp_storage | Whether the provider is not removed and its latest PDP product event is not a removal.
-- asset.column = service_url | Service endpoint URL decoded from capabilities.
-- asset.column = location | Provider location decoded from capabilities.
-- asset.column = location_country_code | Country code parsed from the location DN.
-- asset.column = location_region | State or region parsed from the location DN.
-- asset.column = location_city | City parsed from the location DN.
-- asset.column = payment_token_address | Payment token address from capabilities.
-- asset.column = min_piece_size_bytes | Minimum supported piece size, in bytes.
-- asset.column = max_piece_size_bytes | Maximum supported piece size, in bytes.
-- asset.column = storage_price_per_tib_per_day | Storage price per TiB per day in token base units.
-- asset.column = min_proving_period_epochs | Minimum proving period, in epochs.
-- asset.column = supports_ipni_piece | Whether IPNI piece support is declared.
-- asset.column = supports_ipni_ipfs | Whether IPNI IPFS support is declared.
-- asset.column = ipni_peer_id_hex | Raw hex-encoded IPNI peer id.
-- asset.column = capacity_tib_text | Capacity text from extra capabilities, if any.
-- asset.column = capacity_tib | Parsed numeric capacity, in TiB, if any.
-- asset.column = service_status | Service status from extra capabilities, if any.
-- asset.column = capabilities_json | Latest active PDP capability key-value pairs.
-- asset.column = registered_block | Registration block number.
-- asset.column = registered_transaction_hash | Registration transaction hash.
-- asset.column = registered_at | UTC registration timestamp.
-- asset.column = product_updated_block | Latest PDP product lifecycle block.
-- asset.column = product_updated_transaction_hash | Latest PDP product lifecycle transaction hash.
-- asset.column = product_updated_at | UTC latest PDP product lifecycle timestamp.
-- asset.column = is_fwss_approved | Whether the latest FWSS approval event is approved.
-- asset.column = fwss_first_approved_block | First FWSS approval block, if any.
-- asset.column = fwss_first_approved_at | UTC first FWSS approval timestamp, if any.
-- asset.column = fwss_last_approval_block | Latest FWSS approval block, if any.
-- asset.column = fwss_last_approval_transaction_hash | Latest FWSS approval transaction hash, if any.
-- asset.column = fwss_last_approval_at | UTC latest FWSS approval timestamp, if any.
-- asset.column = registry_snapshot_block | Chain block used for name, description, active, and endorsement state.
-- asset.column = registry_fetched_at | UTC registry snapshot fetch timestamp.

-- asset.not_null = provider_id
-- asset.unique = provider_id

select *
from model.foc_providers
order by provider_id
