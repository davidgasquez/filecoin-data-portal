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
)

select
    deal_id,
    state_root,
    piece_cid,
    padded_piece_size as padded_piece_size_bytes,
    padded_piece_size / pow(1024, 4) as padded_piece_size_tib,
    unpadded_piece_size as unpadded_piece_size_bytes,
    unpadded_piece_size / pow(1024, 4) as unpadded_piece_size_tib,
    is_verified,
    client_id,
    provider_id,
    height as proposed_at_height,
    to_timestamp(height * 30 + 1598306400)::timestamp as proposed_at,
    start_epoch,
    to_timestamp(start_epoch * 30 + 1598306400)::timestamp as start_at,
    end_epoch,
    to_timestamp(end_epoch * 30 + 1598306400)::timestamp as end_at,
    sector_start_epoch,
    to_timestamp(sector_start_epoch * 30 + 1598306400)::timestamp as sector_start_at,
    slash_epoch,
    to_timestamp(slash_epoch * 30 + 1598306400)::timestamp as slash_at,
    storage_price_per_epoch::bigint,
    provider_collateral::bigint,
    client_collateral::bigint,
    label,
    if(sector_start_epoch > 0 and slash_epoch is null and to_timestamp(end_epoch * 30 + 1598306400) > get_current_timestamp(), true, false) as is_active
from base
