# ruff: noqa: E501
# asset.description = Current Filecoin storage provider power from the latest Lily power actor claims snapshot, restricted to providers with positive power.
# asset.materialization = custom
# asset.column = provider_id | Filecoin storage provider miner actor id address.
# asset.column = current_raw_power_tibs | Latest observed raw byte power for the provider, in tebibytes.
# asset.column = current_quality_adjusted_power_tibs | Latest observed quality adjusted power for the provider, in tebibytes.
# asset.column = has_current_power | Whether the provider currently has positive raw or quality adjusted power.
# asset.not_null = provider_id
# asset.not_null = current_raw_power_tibs
# asset.not_null = current_quality_adjusted_power_tibs
# asset.not_null = has_current_power
# asset.unique = provider_id
# asset.assert = current_raw_power_tibs >= 0
# asset.assert = current_quality_adjusted_power_tibs >= 0
# asset.assert = current_raw_power_tibs > 0 or current_quality_adjusted_power_tibs > 0

from fdp.bigquery import materialize_query

ASSET_KEY = "raw.storage_provider_current_power"
SCHEMA = "raw"
QUERY = """
select
    miner_id as provider_id,
    cast(raw_byte_power as float64) / pow(1024, 4) as current_raw_power_tibs,
    cast(quality_adj_power as float64) / pow(1024, 4) as current_quality_adjusted_power_tibs,
    true as has_current_power
from `lily-data.lily.power_actor_claims`
qualify row_number() over (
    partition by miner_id
    order by height desc
) = 1
and (
    cast(raw_byte_power as int64) > 0
    or cast(quality_adj_power as int64) > 0
)
order by provider_id
""".strip()


def current_power() -> None:
    materialize_query(ASSET_KEY, QUERY, schema=SCHEMA)
