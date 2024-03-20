import io
import json

import pandas as pd
import requests
from dagster import ConfigurableResource
from requests import Response
from databricks import sql
from databricks.sql.client import Connection


class SpacescopeResource(ConfigurableResource):
    """
    Spacescope API resource.
    """

    SPACESCOPE_TOKEN: str
    ENDPOINT: str = "https://api.spacescope.io/v2/"

    def request(self, method: str, params: dict = {}) -> Response:
        endpoint = f"{self.ENDPOINT}/{method}"
        headers = {"Authorization": f"Bearer {self.SPACESCOPE_TOKEN}"}

        r = requests.get(
            endpoint,
            headers=headers,
            params=params,
        )

        if r.status_code != 200:
            raise Exception(
                f"API returned {r.status_code} with message: {r.json()['message']}"
            )

        return r

    def get_storage_provider_power(self, storage_provider=None, date=None):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(method="storage_provider/power", params=params).json()
        return r["data"]

    def get_storage_provider_token_balance(self, storage_provider=None, date=None):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(method="storage_provider/token_balance", params=params).json()
        return r["data"]


class DuneResource(ConfigurableResource):
    """
    Dune API resource.
    """

    DUNE_API_KEY: str

    def upload_df(self, df: pd.DataFrame, name: str) -> requests.Response:
        """
        Uploads a DataFrame file to Dune's API.

        Args:
            df (pd.DataFrame): The DataFrame to upload.
            name (str): The name of the table to create.
        """

        url = "https://api.dune.com/api/v1/table/upload/csv"

        file_buffer = io.StringIO()
        df.to_csv(file_buffer, index=False)
        file_buffer.seek(0)
        df_csv = file_buffer.getvalue()

        headers = {"X-Dune-Api-Key": self.DUNE_API_KEY}
        payload = {
            "table_name": name,
            "is_private": False,
            "data": df_csv,
        }

        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()

        return response


class StarboardDatabricksResource(ConfigurableResource):
    DATABRICKS_SERVER_HOSTNAME: str
    DATABRICKS_HTTP_PATH: str
    DATABRICKS_ACCESS_TOKEN: str

    def get_connection(self) -> Connection:
        conn = sql.connect(
            server_hostname=self.DATABRICKS_SERVER_HOSTNAME,
            http_path=self.DATABRICKS_HTTP_PATH,
            access_token=self.DATABRICKS_ACCESS_TOKEN,
        )

        return conn
