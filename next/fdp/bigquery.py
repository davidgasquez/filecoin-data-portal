import os

import pyarrow as pa
from google.cloud import bigquery

from fdp.api import db_connection
from fdp.google import credentials_from_env

DEFAULT_PROJECT = "protocol-labs-data-nexus"
DEFAULT_LOCATION = "us-east4"


def query_arrow(
    query: str,
    *,
    project: str | None = None,
    location: str | None = None,
) -> pa.Table:
    client = bigquery_client(project=project, location=location)
    job_config = bigquery.QueryJobConfig(
        priority=bigquery.QueryPriority.BATCH,
        allow_large_results=True,
    )
    query_job = client.query(query, job_config=job_config)
    return query_job.to_arrow(create_bqstorage_client=True)


def materialize_query(
    asset_key: str,
    query: str,
    *,
    schema: str,
    project: str | None = None,
    location: str | None = None,
) -> int:
    arrow_table = query_arrow(query, project=project, location=location)
    with db_connection() as conn:
        conn.execute(f"create schema if not exists {schema}")
        conn.register("bigquery_result", arrow_table)
        conn.execute(
            f"create or replace table {asset_key} as select * from bigquery_result"
        )
    return arrow_table.num_rows


def bigquery_client(
    *,
    project: str | None = None,
    location: str | None = None,
) -> bigquery.Client:
    credentials = credentials_from_env()
    return bigquery.Client(
        project=project or os.environ.get("FDP_BIGQUERY_PROJECT", DEFAULT_PROJECT),
        location=location or os.environ.get("FDP_BIGQUERY_LOCATION", DEFAULT_LOCATION),
        credentials=credentials,
    )
