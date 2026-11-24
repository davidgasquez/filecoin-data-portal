import base64
import json
import os

import pyarrow as pa
from google.cloud import bigquery
from google.oauth2 import service_account

CREDENTIALS_ENV_VAR = "ENCODED_GOOGLE_APPLICATION_CREDENTIALS"


def credentials_from_env() -> service_account.Credentials:
    encoded = os.environ.get(CREDENTIALS_ENV_VAR)
    if not encoded:
        raise ValueError(f"Missing {CREDENTIALS_ENV_VAR} in environment")

    try:
        payload = json.loads(base64.b64decode(encoded))
    except Exception as exc:
        raise ValueError(f"Invalid {CREDENTIALS_ENV_VAR} payload") from exc

    if not isinstance(payload, dict):
        raise ValueError(f"Invalid {CREDENTIALS_ENV_VAR} payload")

    return service_account.Credentials.from_service_account_info(payload)


def query_arrow(query: str) -> pa.Table:
    client = bigquery.Client(credentials=credentials_from_env())
    job_config = bigquery.QueryJobConfig(
        priority=bigquery.QueryPriority.BATCH, default_dataset="lily-data.lily"
    )
    return client.query(query, job_config=job_config).to_arrow(
        create_bqstorage_client=True
    )
