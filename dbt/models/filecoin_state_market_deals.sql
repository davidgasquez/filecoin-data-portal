with base as (
    select
        DealID,
        Proposal.*,
        State.*
    from {{ source('raw_assets', 'raw_filecoin_state_market_deals') }}
)

select
    dealid as deal_id,
    piececid."/" as piece_cid,
    piecesize as piece_size_bytes,
    piecesize / pow(1024, 4) as piece_size_tibs,
    verifieddeal as is_verified,
    client as client_id,
    provider as provider_id,
    label as label,
    startepoch as start_epoch,
    to_timestamp(startepoch * 30 + 1598306400) as start_at,
    endepoch as end_epoch,
    to_timestamp(endepoch * 30 + 1598306400) as end_at,
    storagepriceperepoch as storage_price_per_epoch,
    providercollateral as provider_collateral,
    clientcollateral as client_collateral,
    sectorstartepoch as sector_start_epoch,
    to_timestamp(sectorstartepoch * 30 + 1598306400) as sector_start_at,
    lastupdatedepoch as last_updated_epoch,
    to_timestamp(lastupdatedepoch * 30 + 1598306400) as last_updated_at,
    slashepoch as slash_epoch,
    to_timestamp(slashepoch * 30 + 1598306400) as slash_at,
    verifiedclaim as verified_claim,
    if(slash_epoch = -1 and to_timestamp(endepoch * 30 + 1598306400) > get_current_timestamp(), true, false) as is_active
from base
