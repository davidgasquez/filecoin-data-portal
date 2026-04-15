-- asset.description = Storage providers with market deal activity.

-- asset.resource = bigquery.lily

-- asset.column = provider_id | Filecoin storage provider actor id address.
-- asset.column = first_market_deal_start_date | First observed market deal start date.
-- asset.column = last_market_deal_start_date | Most recent market deal start date.

-- asset.not_null = provider_id
-- asset.not_null = first_market_deal_start_date
-- asset.not_null = last_market_deal_start_date
-- asset.unique = provider_id
-- asset.assert = first_market_deal_start_date <= last_market_deal_start_date

select
    provider_id,
    min(date(timestamp_seconds((start_epoch * 30) + 1598306400)))
        as first_market_deal_start_date,
    max(date(timestamp_seconds((start_epoch * 30) + 1598306400)))
        as last_market_deal_start_date
from `market_deal_proposals`
group by 1
