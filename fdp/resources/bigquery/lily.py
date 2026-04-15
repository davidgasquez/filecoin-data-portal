import pyarrow as pa
from google.cloud import bigquery

from fdp.google import credentials_from_env

DEFAULT_DATASET = "lily-data.lily"
__all__ = ["query_arrow"]


def query_arrow(query: str) -> pa.Table:
    client = bigquery.Client(credentials=credentials_from_env())
    job_config = bigquery.QueryJobConfig(
        priority=bigquery.QueryPriority.BATCH,
        default_dataset=DEFAULT_DATASET,
        use_query_cache=True,
    )
    query_job = client.query(query, job_config=job_config)
    return query_job.to_arrow(create_bqstorage_client=True)
