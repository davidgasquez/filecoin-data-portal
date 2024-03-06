import os
import json

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

    def upload_csv(self, csv_file_path: str) -> requests.Response:
        """
        Uploads a CSV file to Dune's API.

        Args:
            csv_file_path (str): The path to the CSV file to upload.
        """

        url = "https://api.dune.com/api/v1/table/upload/csv"

        with open(csv_file_path) as open_file:
            data = open_file.read()

            headers = {"X-Dune-Api-Key": self.DUNE_API_KEY}

            payload = {
                "table_name": "example_table",
                "description": "test_description",
                "is_private": False,
                "data": str(data),
            }

            response = requests.post(url, data=json.dumps(payload), headers=headers)

            print("Response status code:", response.status_code)
            print("Response content:", response.content)

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
