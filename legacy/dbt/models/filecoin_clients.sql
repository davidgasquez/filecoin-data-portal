with base_clients as (
    select
        distinct nullif(trim(addressid), '') as client_id
    from {{ source("raw_assets", "raw_datacapstats_verified_clients") }}
    where client_id is not null
    union
    select
        distinct client_id
    from {{ ref("filecoin_state_market_deals") }}
    where client_id is not null
),

state_market_deals_metrics as (
    select distinct
        client_id,
        count(distinct deal_id) as total_deals,
        count(distinct deal_id) filter (where is_verified) as total_verified_deals,
        count(distinct deal_id) filter (where is_active) as total_active_deals,
        count(distinct deal_id) filter (where is_active and is_verified) as total_active_verified_deals,

        count(distinct piece_cid) as total_unique_piece_cids,
        count(distinct piece_cid) filter (where is_verified) as total_verified_unique_piece_cids,
        count(distinct piece_cid) filter (where is_active) as total_active_unique_piece_cids,
        count(distinct piece_cid) filter (where is_active and is_verified) as total_active_verified_unique_piece_cids,

        sum(unpadded_piece_size_tibs) as total_data_uploaded_tibs,
        sum(unpadded_piece_size_tibs) filter (where is_active) as total_active_data_uploaded_tibs,
        sum(unpadded_piece_size_tibs) filter (piece_provider_replication_order = 1) as unique_data_uploaded_tibs,
        sum(unpadded_piece_size_tibs) filter (where is_active and piece_provider_replication_order = 1) as unique_active_data_uploaded_tibs,
        unique_data_uploaded_tibs / sum(unpadded_piece_size_tibs) as unique_data_uploaded_percentage,

        count(distinct provider_id) as total_unique_providers,
        array_agg(distinct provider_id) as provider_ids,
        count(distinct provider_id) filter (where is_active) as total_active_unique_providers,
        array_agg(distinct provider_id) filter (where is_active) as active_provider_ids,
        count(distinct provider_id) filter (where is_active and is_verified) as total_active_verified_unique_providers,

        min(sector_start_at) as first_deal_at,
        min(case when is_active then sector_start_at else null end) as first_active_deal_at,
        max(sector_start_at) as last_deal_at,
        max(case when is_active then sector_start_at else null end) as last_active_deal_at,

        sum(unpadded_piece_size_tibs) filter(where sector_start_at > current_date() - interval '30 days') as data_uploaded_tibs_30d,
        sum(unpadded_piece_size_tibs) filter(where sector_start_at > current_date() - interval '6 months') as data_uploaded_tibs_6m,
        sum(unpadded_piece_size_tibs) filter(where sector_start_at > current_date() - interval '1 year') as data_uploaded_tibs_1y,

        sum(unpadded_piece_size_tibs) filter(where end_at between current_date() - interval '30 days' and current_date()) as data_expired_tibs_30d,
        sum(unpadded_piece_size_tibs) filter(where end_at between current_date() - interval '6 months' and current_date()) as data_expired_tibs_6m,
        sum(unpadded_piece_size_tibs) filter(where end_at between current_date() - interval '1 year' and current_date()) as data_expired_tibs_1y,
    from {{ ref("filecoin_state_market_deals") }}
    where sector_start_epoch is not null
    group by 1
),

datacap_clients as (
    select distinct
        addressid as client_id,
        nullif(address, '') as client_address,
        nullif(name, '') as client_name,
        orgname as organization_name,
        nullif(region, '') as region,
        nullif(industry, '') as industry,
        initialallowance::bigint as initial_datacap_bytes,
        initialallowance::bigint / power(1024, 4) as initial_datacap_tibs,
        coalesce(try_cast(allowance as numeric), 0) as current_datacap_bytes,
        coalesce(try_cast(allowance as numeric), 0) / power(1024, 4) as current_datacap_tibs,
        verifieraddressid as allocator_id,
        nullif(verifiername, '') as verifier_name,
        try_cast(dealcount as int) as datacap_deal_count,
        try_cast(providercount as int) as datacap_provider_count,
        nullif(topprovider, '') as top_provider,
        try_cast(receiveddatacapchange as bigint) as received_datacap_change_bytes,
        try_cast(receiveddatacapchange as bigint) / power(1024, 4) as received_datacap_change_tibs,
        try_cast(useddatacapchange as bigint) as used_datacap_change_bytes,
        try_cast(useddatacapchange as bigint) / power(1024, 4) as used_datacap_change_tibs,
        try_cast(receiveddatacapchange90days as bigint) as received_datacap_change_90d_bytes,
        try_cast(receiveddatacapchange90days as bigint) / power(1024, 4) as received_datacap_change_90d_tibs,
        try_cast(useddatacapchange90days as bigint) as used_datacap_change_90d_bytes,
        try_cast(useddatacapchange90days as bigint) / power(1024, 4) as used_datacap_change_90d_tibs,
        try_cast(useddatacap as bigint) as used_datacap_bytes,
        try_cast(useddatacap as bigint) / power(1024, 4) as used_datacap_tibs,
        try_cast(remainingdatacap as bigint) as reported_remaining_datacap_bytes,
        try_cast(remainingdatacap as bigint) / power(1024, 4) as reported_remaining_datacap_tibs,
        to_timestamp(try_cast(issuecreatetimestamp as numeric)) as datacap_issue_created_at,
        to_timestamp(try_cast(createmessagetimestamp as numeric)) as datacap_message_created_at,
        retries as datacap_retries,
    from {{ source("raw_assets", "raw_datacapstats_verified_clients") }}
    qualify row_number() over (partition by addressid order by createdatheight desc) = 1
),

datacap_github_applications as (
    select
        id as client_address,
        client->>'$.Name' as client_name,
        client->>'$.Region' as client_region,
        client->>'$.Industry' as client_industry,
        client->>'$.Website' as client_website,
        client->>'$.Social Media' as client_social_media,
        client->>'$.Social Media Type' as client_social_media_type,
        client->>'$.Role' as client_role,
    from {{ source("raw_assets", "raw_datacap_github_applications") }}
    qualify row_number() over (partition by id order by version desc) = 1
)

select
    b.client_id,
    m.total_deals,
    m.total_verified_deals,
    m.total_active_deals,
    m.total_active_verified_deals,
    m.total_unique_piece_cids,
    m.total_verified_unique_piece_cids,
    m.total_active_unique_piece_cids,
    m.total_active_verified_unique_piece_cids,
    m.total_data_uploaded_tibs,
    m.total_active_data_uploaded_tibs,
    m.unique_data_uploaded_tibs,
    m.unique_active_data_uploaded_tibs,
    m.unique_data_uploaded_percentage,
    m.total_unique_providers,
    m.provider_ids,
    m.total_active_unique_providers,
    m.active_provider_ids,
    m.total_active_verified_unique_providers,
    m.first_deal_at,
    m.first_active_deal_at,
    m.last_deal_at,
    m.last_active_deal_at,
    m.data_uploaded_tibs_30d,
    m.data_uploaded_tibs_6m,
    m.data_uploaded_tibs_1y,
    m.data_expired_tibs_30d,
    m.data_expired_tibs_6m,
    m.data_expired_tibs_1y,
    c.client_address,
    coalesce(c.client_name, g.client_name) as client_name,
    c.organization_name,
    coalesce(c.region, g.client_region) as region,
    coalesce(c.industry, g.client_industry) as industry,
    g.client_website,
    g.client_social_media,
    g.client_social_media_type,
    g.client_role,
    c.initial_datacap_bytes,
    c.initial_datacap_tibs,
    c.current_datacap_bytes,
    c.current_datacap_tibs,
    c.allocator_id,
    c.verifier_name,
    c.datacap_deal_count,
    c.datacap_provider_count,
    c.top_provider,
    c.received_datacap_change_bytes,
    c.received_datacap_change_tibs,
    c.used_datacap_change_bytes,
    c.used_datacap_change_tibs,
    c.received_datacap_change_90d_bytes,
    c.received_datacap_change_90d_tibs,
    c.used_datacap_change_90d_bytes,
    c.used_datacap_change_90d_tibs,
    c.used_datacap_bytes,
    c.used_datacap_tibs,
    c.reported_remaining_datacap_bytes,
    c.reported_remaining_datacap_tibs,
    c.datacap_issue_created_at,
    c.datacap_message_created_at,
    c.datacap_retries
from base_clients as b
left join state_market_deals_metrics as m on m.client_id = b.client_id
left join datacap_clients c on c.client_id = b.client_id
left join datacap_github_applications g on g.client_address = c.client_address
order by last_deal_at desc
