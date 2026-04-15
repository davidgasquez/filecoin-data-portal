-- asset.description = Mainnet Filecoin service providers reconstructed from ServiceProviderRegistry and FWSS events. Includes registry identity, event-derived PDP offering state, parsed capability fields, and FWSS approval status.

-- asset.depends = raw.fevm_eth_logs_decoded

-- asset.column = provider_id | Service provider registry identifier.
-- asset.column = service_provider | Provider control address recorded at registration.
-- asset.column = payee | Payee address recorded at registration.
-- asset.column = is_registered | Whether the provider has a ProviderRegistered event.
-- asset.column = is_removed | Whether the provider has a ProviderRemoved event.
-- asset.column = is_active | Event-derived registry activity flag based on registration, removal, and PDP product removal state.
-- asset.column = product_type | Latest PDP product type label from registry product lifecycle events.
-- asset.column = offers_pdp_storage | Whether the latest PDP product lifecycle event indicates an active PDP offering.
-- asset.column = service_url | PDP service endpoint URL decoded from capability bytes.
-- asset.column = location | PDP provider location in DN format decoded from capability bytes.
-- asset.column = location_country_code | Country code parsed from the decoded location DN.
-- asset.column = location_region | State or region parsed from the decoded location DN.
-- asset.column = location_city | City parsed from the decoded location DN.
-- asset.column = payment_token_address | Payment token address declared in PDP capabilities.
-- asset.column = min_piece_size_bytes | Minimum supported piece size in bytes declared in PDP capabilities.
-- asset.column = max_piece_size_bytes | Maximum supported piece size in bytes declared in PDP capabilities.
-- asset.column = storage_price_per_tib_per_day | Storage price per TiB per day in token base units declared in PDP capabilities.
-- asset.column = min_proving_period_epochs | Minimum proving period in epochs declared in PDP capabilities.
-- asset.column = supports_ipni_piece | Whether PDP capabilities declare IPNI piece support.
-- asset.column = supports_ipni_ipfs | Whether PDP capabilities declare IPNI IPFS support.
-- asset.column = ipni_peer_id_hex | Raw hex-encoded IPNI peer id bytes from PDP capabilities.
-- asset.column = capacity_tib_text | Optional capacity text declared in extra PDP capabilities.
-- asset.column = capacity_tib | Numeric capacity parsed from capacity_tib_text when possible.
-- asset.column = service_status | Optional service status decoded from extra PDP capabilities.
-- asset.column = capabilities_json | JSON object of the latest active PDP capability key-value pairs with raw hex values.
-- asset.column = registered_block | Block where the provider was registered.
-- asset.column = registered_transaction_hash | Transaction hash of the registration event.
-- asset.column = registered_date | UTC date derived from the registration block.
-- asset.column = product_last_updated_block | Block of the latest PDP product lifecycle event.
-- asset.column = product_last_updated_transaction_hash | Transaction hash of the latest PDP product lifecycle event.
-- asset.column = product_last_updated_date | UTC date derived from the latest PDP product lifecycle event block.
-- asset.column = is_fwss_approved | Whether the latest FWSS provider approval lifecycle event indicates the provider is approved.
-- asset.column = fwss_first_approved_block | First block where FWSS approved the provider, if any.
-- asset.column = fwss_first_approved_date | UTC date derived from the first FWSS approval block, if any.
-- asset.column = fwss_last_approval_block | Block of the latest FWSS provider approval lifecycle event, if any.
-- asset.column = fwss_last_approval_transaction_hash | Transaction hash of the latest FWSS provider approval lifecycle event, if any.
-- asset.column = fwss_last_approval_date | UTC date derived from the latest FWSS provider approval lifecycle event block, if any.

-- asset.not_null = provider_id
-- asset.unique = provider_id

with params as (
    select 1598306400 as genesis_timestamp
),
provider_registered as (
    select
        cast(json_extract_string(args, '$.providerId') as bigint) as provider_id,
        lower(json_extract_string(args, '$.serviceProvider')) as service_provider,
        lower(json_extract_string(args, '$.payee')) as payee,
        block_number as registered_block,
        log_index as registered_log_index,
        transaction_hash as registered_transaction_hash,
        date(to_timestamp(block_number * 30 + (select genesis_timestamp from params))) as registered_date,
        row_number() over (
            partition by cast(json_extract_string(args, '$.providerId') as bigint)
            order by block_number, log_index
        ) as row_num
    from raw.fevm_eth_logs_decoded
    where abi_name = 'service_provider_registry'
      and event_name = 'ProviderRegistered'
),
provider_removed as (
    select
        cast(json_extract_string(args, '$.providerId') as bigint) as provider_id,
        block_number as removed_block,
        log_index as removed_log_index,
        transaction_hash as removed_transaction_hash,
        date(to_timestamp(block_number * 30 + (select genesis_timestamp from params))) as removed_date,
        row_number() over (
            partition by cast(json_extract_string(args, '$.providerId') as bigint)
            order by block_number, log_index
        ) as row_num
    from raw.fevm_eth_logs_decoded
    where abi_name = 'service_provider_registry'
      and event_name = 'ProviderRemoved'
),
product_events as (
    select
        cast(json_extract_string(args, '$.providerId') as bigint) as provider_id,
        cast(json_extract_string(args, '$.productType') as integer) as product_type,
        event_name,
        block_number,
        log_index,
        transaction_hash,
        args,
        date(to_timestamp(block_number * 30 + (select genesis_timestamp from params))) as event_date,
        row_number() over (
            partition by cast(json_extract_string(args, '$.providerId') as bigint), cast(json_extract_string(args, '$.productType') as integer)
            order by block_number desc, log_index desc
        ) as row_num
    from raw.fevm_eth_logs_decoded
    where abi_name = 'service_provider_registry'
      and event_name in ('ProductAdded', 'ProductUpdated', 'ProductRemoved')
),
latest_pdp_product as (
    select
        provider_id,
        product_type,
        event_name,
        block_number as product_last_updated_block,
        log_index as product_last_updated_log_index,
        transaction_hash as product_last_updated_transaction_hash,
        event_date as product_last_updated_date,
        args
    from product_events
    where row_num = 1
      and product_type = 0
),
latest_pdp_capabilities as (
    select
        products.provider_id,
        json_extract_string(keys.value, '$') as capability_key,
        lower(json_extract_string(keys.value, '$')) as capability_key_normalized,
        json_extract_string(values.value, '$') as capability_value
    from latest_pdp_product as products,
        json_each(json_extract(products.args, '$.capabilityKeys')) as keys,
        json_each(json_extract(products.args, '$.capabilityValues')) as values
    where products.event_name != 'ProductRemoved'
      and keys.key = values.key
),
provider_capabilities as (
    select
        provider_id,
        json_group_object(capability_key, capability_value) as capabilities_json,
        max(case
            when capability_key_normalized = 'serviceurl' and capability_value like '0x%'
                then cast(from_hex(substr(capability_value, 3)) as varchar)
        end) as service_url,
        max(case
            when capability_key_normalized = 'location' and capability_value like '0x%'
                then cast(from_hex(substr(capability_value, 3)) as varchar)
        end) as location,
        max(case
            when capability_key_normalized = 'paymenttokenaddress'
                then lower(capability_value)
        end) as payment_token_address,
        max(case
            when capability_key_normalized = 'minpiecesizeinbytes'
                then try_cast(capability_value as bigint)
        end) as min_piece_size_bytes,
        max(case
            when capability_key_normalized = 'maxpiecesizeinbytes'
                then try_cast(capability_value as bigint)
        end) as max_piece_size_bytes,
        max(case
            when capability_key_normalized = 'storagepricepertibperday'
                then try_cast(capability_value as bigint)
        end) as storage_price_per_tib_per_day,
        max(case
            when capability_key_normalized = 'minprovingperiodinepochs'
                then try_cast(capability_value as bigint)
        end) as min_proving_period_epochs,
        max(case
            when capability_key_normalized = 'ipnipiece'
                then lower(capability_value) in ('0x1', '0x01')
        end) as supports_ipni_piece,
        max(case
            when capability_key_normalized = 'ipniipfs'
                then lower(capability_value) in ('0x1', '0x01')
        end) as supports_ipni_ipfs,
        max(case
            when capability_key_normalized = 'ipnipeerid'
                then lower(capability_value)
        end) as ipni_peer_id_hex,
        max(case
            when capability_key_normalized = 'capacitytib' and capability_value like '0x%'
                then cast(from_hex(substr(capability_value, 3)) as varchar)
        end) as capacity_tib_text,
        max(case
            when capability_key_normalized = 'capacitytib' and capability_value like '0x%'
                then try_cast(
                    nullif(
                        regexp_extract(cast(from_hex(substr(capability_value, 3)) as varchar), '([0-9]+(?:\\.[0-9]+)?)', 1),
                        ''
                    ) as double
                )
        end) as capacity_tib,
        max(case
            when capability_key_normalized = 'servicestatus' and capability_value like '0x%'
                then cast(from_hex(substr(capability_value, 3)) as varchar)
        end) as service_status
    from latest_pdp_capabilities
    group by 1
),
fwss_approval_events as (
    select
        cast(json_extract_string(args, '$.providerId') as bigint) as provider_id,
        event_name,
        block_number,
        log_index,
        transaction_hash,
        date(to_timestamp(block_number * 30 + (select genesis_timestamp from params))) as event_date,
        row_number() over (
            partition by cast(json_extract_string(args, '$.providerId') as bigint)
            order by block_number desc, log_index desc
        ) as latest_row_num,
        row_number() over (
            partition by cast(json_extract_string(args, '$.providerId') as bigint)
            order by case when event_name = 'ProviderApproved' then block_number end, case when event_name = 'ProviderApproved' then log_index end
        ) as first_approved_row_num
    from raw.fevm_eth_logs_decoded
    where abi_name = 'filecoin_warm_storage_service'
      and event_name in ('ProviderApproved', 'ProviderUnapproved')
),
fwss_latest_approval as (
    select
        provider_id,
        event_name = 'ProviderApproved' as is_fwss_approved,
        block_number as fwss_last_approval_block,
        transaction_hash as fwss_last_approval_transaction_hash,
        event_date as fwss_last_approval_date
    from fwss_approval_events
    where latest_row_num = 1
),
fwss_first_approval as (
    select
        provider_id,
        block_number as fwss_first_approved_block,
        event_date as fwss_first_approved_date
    from (
        select
            provider_id,
            block_number,
            event_date,
            row_number() over (
                partition by provider_id
                order by block_number, log_index
            ) as row_num
        from fwss_approval_events
        where event_name = 'ProviderApproved'
    )
    where row_num = 1
)
select
    registered.provider_id,
    registered.service_provider,
    registered.payee,
    true as is_registered,
    removed.provider_id is not null as is_removed,
    removed.provider_id is null
        and coalesce(products.event_name, 'ProductRemoved') != 'ProductRemoved' as is_active,
    case products.product_type
        when 0 then 'PDP'
        else cast(products.product_type as varchar)
    end as product_type,
    coalesce(products.event_name != 'ProductRemoved', false) as offers_pdp_storage,
    capabilities.service_url,
    capabilities.location,
    nullif(regexp_extract(capabilities.location, '(^|;)C=([^;]+)', 2), '') as location_country_code,
    nullif(regexp_extract(capabilities.location, '(^|;)ST=([^;]+)', 2), '') as location_region,
    nullif(regexp_extract(capabilities.location, '(^|;)L=([^;]+)', 2), '') as location_city,
    capabilities.payment_token_address,
    capabilities.min_piece_size_bytes,
    capabilities.max_piece_size_bytes,
    capabilities.storage_price_per_tib_per_day,
    capabilities.min_proving_period_epochs,
    capabilities.supports_ipni_piece,
    capabilities.supports_ipni_ipfs,
    capabilities.ipni_peer_id_hex,
    capabilities.capacity_tib_text,
    capabilities.capacity_tib,
    capabilities.service_status,
    capabilities.capabilities_json,
    registered.registered_block,
    registered.registered_transaction_hash,
    registered.registered_date,
    products.product_last_updated_block,
    products.product_last_updated_transaction_hash,
    products.product_last_updated_date,
    coalesce(fwss_latest.is_fwss_approved, false) as is_fwss_approved,
    fwss_first.fwss_first_approved_block,
    fwss_first.fwss_first_approved_date,
    fwss_latest.fwss_last_approval_block,
    fwss_latest.fwss_last_approval_transaction_hash,
    fwss_latest.fwss_last_approval_date
from provider_registered as registered
left join provider_removed as removed
    on registered.provider_id = removed.provider_id
   and removed.row_num = 1
left join latest_pdp_product as products
    on registered.provider_id = products.provider_id
left join provider_capabilities as capabilities
    on registered.provider_id = capabilities.provider_id
left join fwss_latest_approval as fwss_latest
    on registered.provider_id = fwss_latest.provider_id
left join fwss_first_approval as fwss_first
    on registered.provider_id = fwss_first.provider_id
where registered.row_num = 1
order by registered.provider_id
