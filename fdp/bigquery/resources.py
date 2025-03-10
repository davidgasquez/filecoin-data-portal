import dagster as dg
import pyarrow as pa
import pyarrow.dataset as ds
from dagster_gcp import BigQueryResource
from dagster_gcp.bigquery.utils import setup_gcp_creds
from google.cloud import bigquery, bigquery_storage


class BigQueryArrowResource(BigQueryResource):
    """
    A wrapper around the BigQueryResource to return pyarrow scanners.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def query_to_scanner(self, query: str, schema: pa.Schema) -> ds.Scanner:
        job_config = bigquery.QueryJobConfig(
            priority=bigquery.QueryPriority.BATCH,
            allow_large_results=True,
        )

        with setup_gcp_creds(str(self.gcp_credentials)):
            bq_storage_client = bigquery_storage.BigQueryReadClient()

        with self.get_client() as client:
            query_job = client.query(query, job_config=job_config)
            results = query_job.result()

            arrow_batches = results.to_arrow_iterable(bq_storage_client)

        return ds.Scanner.from_batches(arrow_batches, schema=schema)


lily_bigquery = BigQueryArrowResource(
    project="protocol-labs-data-nexus",
    location="us-east4",
    gcp_credentials=dg.EnvVar("ENCODED_GOOGLE_APPLICATION_CREDENTIALS"),
)

fdp_bigquery = BigQueryArrowResource(
    project="protocol-labs-data-nexus",
    gcp_credentials=dg.EnvVar("ENCODED_GOOGLE_APPLICATION_CREDENTIALS"),
)
