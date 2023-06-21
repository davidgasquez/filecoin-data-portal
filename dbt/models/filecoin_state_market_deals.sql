select
    *
from {{ ref('source_filecoin_state_market_deals_source') }}
