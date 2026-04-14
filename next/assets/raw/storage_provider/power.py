# asset.description = Daily end-of-day Filecoin storage provider power
# snapshots derived from Lily power actor claims, with sparse rows only for
# provider-days with positive power.

# asset.materialization = custom

# asset.column = date | UTC day for the end-of-day power snapshot.
# asset.column = provider_id | Filecoin storage provider miner actor id
# address.
# asset.column = raw_power_tibs | End-of-day raw byte power for the provider,
# in tebibytes.
# asset.column = quality_adjusted_power_tibs | End-of-day quality adjusted
# power for the provider, in tebibytes.
# asset.column = has_power | Whether the provider had positive raw or quality
# adjusted power at end of day.

# asset.not_null = date
# asset.not_null = provider_id
# asset.not_null = raw_power_tibs
# asset.not_null = quality_adjusted_power_tibs
# asset.not_null = has_power
# asset.assert = raw_power_tibs > 0
# asset.assert = quality_adjusted_power_tibs >= 0

from fdp.bigquery import materialize_query

ASSET_KEY = "raw.storage_provider_power"
SCHEMA = "raw"
QUERY = """
with provider_daily_power_changes as (
    select
        date(timestamp_seconds((height * 30) + 1598306400)) as date,
        miner_id as provider_id,
        cast(raw_byte_power as int64) as raw_power_bytes,
        cast(raw_byte_power as float64) / pow(1024, 4) as raw_power_tibs,
        cast(quality_adj_power as int64) as quality_adj_power_bytes,
        cast(quality_adj_power as float64) / pow(1024, 4)
            as quality_adjusted_power_tibs
    from `lily-data.lily.power_actor_claims`
    qualify row_number() over (
        partition by date(timestamp_seconds((height * 30) + 1598306400)), miner_id
        order by height desc
    ) = 1
),
latest_observed_day as (
    select max(date) + 1 as next_date
    from provider_daily_power_changes
),
power_intervals as (
    select
        date as start_date,
        coalesce(
            lead(date) over (partition by provider_id order by date),
            (select next_date from latest_observed_day)
        ) as end_date_exclusive,
        provider_id,
        raw_power_bytes,
        raw_power_tibs,
        quality_adj_power_bytes,
        quality_adjusted_power_tibs
    from provider_daily_power_changes
)
select
    day as date,
    provider_id,
    raw_power_tibs,
    quality_adjusted_power_tibs,
    true as has_power
from power_intervals,
unnest(
    generate_date_array(start_date, date_sub(end_date_exclusive, interval 1 day))
) as day
where raw_power_bytes > 0
   or quality_adj_power_bytes > 0
order by 1, 2
""".strip()


def power() -> None:
    materialize_query(ASSET_KEY, QUERY, schema=SCHEMA)
