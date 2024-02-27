select
    date_trunc('day', start_at) as date,
    provider_id,
    count(distinct deal_id) as proposed_deals,
    sum(padded_piece_size_tib) as proposed_data_tibs
from '../../../data/tables/filecoin_state_market_deals_proposals.parquet'
group by 1, 2
