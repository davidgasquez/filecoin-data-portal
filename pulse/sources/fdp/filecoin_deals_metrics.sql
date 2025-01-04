select
    date_trunc('day', sector_start_at) as date,
    client_id,
    provider_id,
    count(distinct deal_id) as deals,
    sum(padded_piece_size_tibs) as onboarded_data_tibs
from 'https://data.filecoindataportal.xyz/filecoin_state_market_deals.parquet'
where sector_start_at is not null
group by 1, 2, 3
