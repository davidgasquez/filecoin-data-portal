with state_market_deals_metrics as (
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
        count(distinct provider_id) filter (where is_active) as total_active_unique_providers,
        count(distinct provider_id) filter (where is_active and is_verified) as total_active_verified_unique_providers,

        min(sector_start_at) as first_deal_at,
        min(case when is_active then sector_start_at else null end) as first_active_deal_at,
        max(sector_start_at) as last_deal_at,
        max(case when is_active then sector_start_at else null end) as last_active_deal_at,

        sum(unpadded_piece_size_tibs) filter(where sector_start_at > current_date() - interval '30 days') as data_uploaded_tibs_30d,
        sum(unpadded_piece_size_tibs) filter(where sector_start_at > current_date() - interval '6 months') as data_uploaded_tibs_6m,
        sum(unpadded_piece_size_tibs) filter(where sector_start_at > current_date() - interval '1 year') as data_uploaded_tibs_1y,
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
    from {{ source("raw_assets", "raw_datacapstats_verified_clients") }}
    qualify row_number() over (partition by addressid order by createdatheight desc) = 1
)

select
    m.*,
    c.client_address,
    c.client_name,
    c.organization_name,
    c.region,
    c.industry,
    c.initial_datacap_bytes,
    c.initial_datacap_tibs,
    c.current_datacap_bytes,
    c.current_datacap_tibs,
    c.allocator_id
from state_market_deals_metrics m
left join datacap_clients c on m.client_id = c.client_id
