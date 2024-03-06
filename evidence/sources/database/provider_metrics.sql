select
    date_trunc('day', sector_start_at) as date,
    provider_id,
    count(distinct deal_id) as deals,
    sum(padded_piece_size_tib) as onboarded_data_tibs
from filecoin_state_market_deals
where sector_start_at is not null
group by 1, 2
