with base as (
    select
        height,
        deal_id,
        state_root,
        piece_cid,
        padded_piece_size,
        unpadded_piece_size,
        is_verified,
        client_id,
        provider_id,
        start_epoch,
        end_epoch,
        storage_price_per_epoch,
        provider_collateral,
        client_collateral,
        sector_start_epoch,
        slash_epoch
    from {{ source('raw_assets', 'raw_filecoin_state_market_deals') }}
),

replication_factor as (
    select
        piece_cid,
        provider_id,
        client_id,
        sector_start_epoch,
        deal_id,
        count(1) over (partition by piece_cid) as piece_replication_factor,
        row_number() over provider_pieces as piece_provider_replication_order,
        count(1) over provider_pieces as piece_provider_replication_factor,
        row_number() over client_pieces as piece_client_replication_order,
        count(1) over client_pieces as piece_client_replication_factor,
        min(sector_start_epoch) over (partition by piece_cid) as piece_first_sector_start_epoch,
        max(sector_start_epoch) over (partition by piece_cid) as piece_last_sector_start_epoch,
        -- approx_count_distinct(provider_id) over (partition by piece_cid) as piece_distinct_provider_count,
        -- approx_count_distinct(client_id) over (partition by piece_cid) as piece_distinct_client_count
    from base
    where sector_start_epoch > 0
    window
        provider_pieces as (partition by provider_id, piece_cid order by sector_start_epoch),
        client_pieces as (partition by client_id, piece_cid order by sector_start_epoch)
)

select
    b.deal_id,
    state_root,
    b.piece_cid,
    padded_piece_size as padded_piece_size_bytes,
    padded_piece_size / pow(1024, 4) as padded_piece_size_tibs,
    unpadded_piece_size as unpadded_piece_size_bytes,
    unpadded_piece_size / pow(1024, 4) as unpadded_piece_size_tibs,
    is_verified,
    b.client_id,
    b.provider_id,
    height as proposed_epoch,
    to_timestamp(height * 30 + 1598306400)::timestamp as proposed_at,
    start_epoch,
    to_timestamp(start_epoch * 30 + 1598306400)::timestamp as start_at,
    end_epoch,
    to_timestamp(end_epoch * 30 + 1598306400)::timestamp as end_at,
    b.sector_start_epoch,
    to_timestamp(b.sector_start_epoch * 30 + 1598306400)::timestamp as sector_start_at,
    case when slash_epoch = -1 then null else slash_epoch end as slash_epoch,
    case when slash_epoch = -1 then null else to_timestamp(slash_epoch * 30 + 1598306400)::timestamp end as slash_at,
    storage_price_per_epoch::bigint as storage_price_per_epoch,
    storage_price_per_epoch::bigint / pow(10, 18) as storage_price_per_epoch_fil,
    provider_collateral::bigint as provider_collateral,
    client_collateral::bigint as client_collateral,
    if(b.sector_start_epoch > 0 and (slash_epoch is null or slash_epoch = -1) and to_timestamp(end_epoch * 30 + 1598306400) > get_current_timestamp(), true, false) as is_active,
    b.sector_start_epoch - proposed_epoch as activation_epochs_delay,
    b.end_epoch - b.sector_start_epoch as deal_lenght_epochs,
    date_part('day', end_at - sector_start_at) as deal_lenght_days,
    storage_price_per_epoch_fil * deal_lenght_epochs as deal_storage_cost_fil,
    replication_factor.piece_provider_replication_order,
    replication_factor.piece_provider_replication_factor,
    replication_factor.piece_client_replication_order,
    replication_factor.piece_client_replication_factor,
    replication_factor.piece_replication_factor,
    replication_factor.piece_first_sector_start_epoch,
    replication_factor.piece_last_sector_start_epoch,
    -- replication_factor.piece_distinct_provider_count,
    -- replication_factor.piece_distinct_client_count,
    to_timestamp(replication_factor.piece_first_sector_start_epoch * 30 + 1598306400)::timestamp as piece_first_sector_start_at,
    to_timestamp(replication_factor.piece_last_sector_start_epoch * 30 + 1598306400)::timestamp as piece_last_sector_start_at
from base as b
left join replication_factor on b.deal_id = replication_factor.deal_id and b.deal_id = replication_factor.deal_id
