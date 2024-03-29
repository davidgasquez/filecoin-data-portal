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
        label,
        sector_start_epoch,
        slash_epoch
    from {{ source('raw_assets', 'raw_filecoin_state_market_deals') }}
),

replication_factor as (
    select
        provider_id,
        piece_cid,
        sector_start_epoch,
        deal_id,
        row_number() over (partition by provider_id, piece_cid order by sector_start_epoch) as piece_provider_replication_order,
        count(1) over (partition by provider_id, piece_cid) as piece_provider_replication_factor
    from base
    where sector_start_epoch > 0
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
    client_id,
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
    provider_collateral::bigint as provider_collateral,
    client_collateral::bigint as client_collateral,
    label,
    if(b.sector_start_epoch > 0 and (slash_epoch is null or slash_epoch = -1) and to_timestamp(end_epoch * 30 + 1598306400) > get_current_timestamp(), true, false) as is_active,
    b.sector_start_epoch - proposed_epoch as activation_epochs_delay,
    replication_factor.piece_provider_replication_order,
    replication_factor.piece_provider_replication_factor
from base as b
left join replication_factor
    on b.deal_id = replication_factor.deal_id
        and b.provider_id = replication_factor.provider_id
        and b.piece_cid = replication_factor.piece_cid
