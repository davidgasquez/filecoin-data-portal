"""Lily BigQuery queries returned as Arrow tables."""

import pyarrow as pa
from google.cloud import bigquery

from fdp.google import credentials_from_env


def query_arrow(query: str) -> pa.Table:
    client = bigquery.Client(credentials=credentials_from_env())
    job_config = bigquery.QueryJobConfig(
        priority=bigquery.QueryPriority.BATCH, default_dataset="lily-data.lily"
    )
    return client.query(query, job_config=job_config).to_arrow(
        create_bqstorage_client=True
    )
