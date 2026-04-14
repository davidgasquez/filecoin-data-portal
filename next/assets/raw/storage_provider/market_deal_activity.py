# ruff: noqa: E501
# asset.description = Filecoin storage providers with market deal activity from Lily market deal proposals.
# asset.materialization = custom
# asset.column = provider_id | Filecoin storage provider miner actor id address.
# asset.column = first_market_deal_start_date | First observed storage deal start date for the provider.
# asset.column = last_market_deal_start_date | Most recent storage deal start date for the provider.
# asset.not_null = provider_id
# asset.not_null = first_market_deal_start_date
# asset.not_null = last_market_deal_start_date
# asset.unique = provider_id
# asset.assert = first_market_deal_start_date <= last_market_deal_start_date

from fdp.bigquery import materialize_query

ASSET_KEY = "raw.storage_provider_market_deal_activity"
SCHEMA = "raw"
QUERY = """
select
    provider_id,
    min(date(timestamp_seconds((start_epoch * 30) + 1598306400))) as first_market_deal_start_date,
    max(date(timestamp_seconds((start_epoch * 30) + 1598306400))) as last_market_deal_start_date
from `lily-data.lily.market_deal_proposals`
group by 1
order by provider_id
""".strip()


def market_deal_activity() -> None:
    materialize_query(ASSET_KEY, QUERY, schema=SCHEMA)
