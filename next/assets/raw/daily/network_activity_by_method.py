# ruff: noqa: E501
# asset.description = Daily Filecoin onchain activity by method from Lily BigQuery.
# asset.materialization = custom
# asset.not_null = date
# asset.not_null = method

import os

from google.cloud import bigquery

from fdp.api import db_connection
from fdp.google import credentials_from_env

ASSET_KEY = "raw.daily_network_activity_by_method"
SCHEMA = "raw"
DEFAULT_PROJECT = "protocol-labs-data-nexus"
DEFAULT_LOCATION = "us-east4"
QUERY = """
select
    date(timestamp_seconds((height * 30) + 1598306400)) as date,
    concat(regexp_extract(actor_name, r'[^/]+$'), '/', g.method, '/', coalesce(m.method_name, 'unknown')) as method,
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


def materialize_bigquery_asset() -> None:
    client = bigquery.Client(
        project=os.environ.get("FDP_BIGQUERY_PROJECT", DEFAULT_PROJECT),
        location=os.environ.get("FDP_BIGQUERY_LOCATION", DEFAULT_LOCATION),
        credentials=credentials_from_env(),
    )
    job_config = bigquery.QueryJobConfig(
        priority=bigquery.QueryPriority.BATCH,
        allow_large_results=True,
    )
    arrow_table = client.query(QUERY, job_config=job_config).to_arrow(
        create_bqstorage_client=True
    )
    with db_connection() as conn:
        conn.execute(f"create schema if not exists {SCHEMA}")
        conn.register("bigquery_result", arrow_table)
        conn.execute(
            f"create or replace table {ASSET_KEY} as select * from bigquery_result"
        )


def network_activity_by_method() -> None:
    materialize_bigquery_asset()
