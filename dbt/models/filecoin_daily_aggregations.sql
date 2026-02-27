select
    date,
    miner_tip_fil,
    burnt_fil,
    miner_tip_fil + burnt_fil as miner_tips_plus_burnt_fil
from {{ source('raw_assets', 'raw_filecoin_daily_aggregations') }}
order by 1 desc
