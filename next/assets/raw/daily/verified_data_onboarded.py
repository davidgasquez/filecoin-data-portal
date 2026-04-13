# ruff: noqa: E501
# asset.description = Daily total verified data onboarded on Filecoin, derived from verified registry ClaimAllocations execution traces in Lily BigQuery.
# asset.materialization = custom
# asset.column = date | UTC day when verified data was successfully claimed/onboarded.
# asset.column = verified_data_onboarded_bytes | Sum of verified piece sizes claimed on the day, in bytes.
# asset.column = verified_data_onboarded_pibs | Sum of verified piece sizes claimed on the day, in pebibytes.
# asset.column = verified_claims | Number of successful verified registry claims on the day.
# asset.column = unique_clients | Distinct clients with at least one successful verified claim on the day.
# asset.column = unique_providers | Distinct providers with at least one successful verified claim on the day.
# asset.not_null = date
# asset.not_null = verified_data_onboarded_bytes
# asset.not_null = verified_data_onboarded_pibs
# asset.not_null = verified_claims
# asset.not_null = unique_clients
# asset.not_null = unique_providers
# asset.unique = date
# asset.assert = verified_data_onboarded_bytes >= 0
# asset.assert = verified_data_onboarded_pibs >= 0
# asset.assert = verified_claims >= 0
# asset.assert = unique_clients >= 0
# asset.assert = unique_providers >= 0

import os

from google.cloud import bigquery

from fdp.api import db_connection
from fdp.google import credentials_from_env

ASSET_KEY = "raw.daily_verified_data_onboarded"
SCHEMA = "raw"
DEFAULT_PROJECT = "protocol-labs-data-nexus"
DEFAULT_LOCATION = "us-east4"
QUERY = """
with verified_registry_claims as (
    select
        date(timestamp_seconds((v.height * 30) + 1598306400)) as date,
        v.`from` as provider,
        cast(json_extract_scalar(claim, '$.Client') as int64) as client_id,
        cast(json_extract_scalar(claim, '$.Size') as int64) as piece_size_bytes
    from `lily-data.lily.vm_messages` as v
    cross join unnest(coalesce(json_extract_array(v.params, '$.Sectors'), array<string>[])) as sector
    cross join unnest(coalesce(json_extract_array(sector, '$.Claims'), array<string>[])) as claim
    where v.`to` = 'f06'
      and v.method = 9
      and v.exit_code = 0
      and json_extract_scalar(claim, '$.Client') is not null

    union all

    select
        date(timestamp_seconds((v.height * 30) + 1598306400)) as date,
        v.`from` as provider,
        cast(json_extract_scalar(sector, '$.Client') as int64) as client_id,
        cast(json_extract_scalar(sector, '$.Size') as int64) as piece_size_bytes
    from `lily-data.lily.vm_messages` as v
    cross join unnest(coalesce(json_extract_array(v.params, '$.Sectors'), array<string>[])) as sector
    where v.`to` = 'f06'
      and v.method = 9
      and v.exit_code = 0
      and json_extract_scalar(sector, '$.Client') is not null
      and array_length(coalesce(json_extract_array(sector, '$.Claims'), array<string>[])) = 0
)

select
    date,
    sum(piece_size_bytes) as verified_data_onboarded_bytes,
    cast(sum(piece_size_bytes) as float64) / pow(1024, 5) as verified_data_onboarded_pibs,
    count(*) as verified_claims,
    count(distinct client_id) as unique_clients,
    count(distinct provider) as unique_providers
from verified_registry_claims
group by 1
order by 1
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


def verified_data_onboarded() -> None:
    materialize_bigquery_asset()
