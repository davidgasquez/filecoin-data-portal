# asset.description = Daily Filecoin onchain activity by method from Lily BigQuery.

# asset.materialization = custom

# asset.not_null = date
# asset.not_null = method

from fdp.bigquery import materialize_query

ASSET_KEY = "raw.daily_network_activity_by_method"
SCHEMA = "raw"
QUERY = """
select
    date(timestamp_seconds((height * 30) + 1598306400)) as date,
    concat(
        regexp_extract(actor_name, r'[^/]+$'),
        '/',
        g.method,
        '/',
        coalesce(m.method_name, 'unknown')
    ) as method,
    sum(gas_used) / 1e6 as gas_used_millions,
    count(*) as transactions,
    sum(cast(value as numeric) / 1e18) as total_value_fil,
    sum(
        (
            cast(base_fee_burn as numeric)
            + cast(over_estimation_burn as numeric)
            + cast(miner_tip as numeric)
        ) / 1e18
    ) as total_gas_fee_fil
from `lily-data.lily.derived_gas_outputs` as g
left join `lily-data.lily.actor_methods` as m
    on g.method = m.method
   and regexp_extract(g.actor_name, r'[^/]+$') = m.family
group by 1, 2
order by 1 desc, 4 desc
""".strip()


def network_activity_by_method() -> None:
    materialize_query(ASSET_KEY, QUERY, schema=SCHEMA)
