-- asset.description = Storage providers with market deal activity.

-- asset.resource = bigquery.lily

-- asset.column = provider_id | Filecoin storage provider actor id address.
-- asset.column = first_market_deal_start_at | First observed market deal start timestamp.
-- asset.column = last_market_deal_start_at | Most recent market deal start timestamp.

-- asset.not_null = provider_id
-- asset.not_null = first_market_deal_start_at
-- asset.not_null = last_market_deal_start_at
-- asset.unique = provider_id
-- asset.assert = first_market_deal_start_at <= last_market_deal_start_at

select
    provider_id,
    min(timestamp_seconds((start_epoch * 30) + 1598306400))
        as first_market_deal_start_at,
    max(timestamp_seconds((start_epoch * 30) + 1598306400))
        as last_market_deal_start_at
from `market_deal_proposals`
group by 1
