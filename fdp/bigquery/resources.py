import dagster as dg
from dagster_gcp import BigQueryResource

lily_bigquery = BigQueryResource(
    project="protocol-labs-data-nexus",
    location="us-east4",
    gcp_credentials=dg.EnvVar("ENCODED_GOOGLE_APPLICATION_CREDENTIALS"),
)

fdp_bigquery = BigQueryResource(
    project="protocol-labs-data-nexus",
    gcp_credentials=dg.EnvVar("ENCODED_GOOGLE_APPLICATION_CREDENTIALS"),
)
