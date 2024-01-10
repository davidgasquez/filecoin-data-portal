import json
import os

import requests
from dagster import ConfigurableResource
from requests import Response


class SpacescopeResource(ConfigurableResource):
    """
    Spacescope API resource.
    """

    token: str = str(os.getenv("SPACESCOPE_TOKEN"))
    endpoint: str = "https://api.spacescope.io/v2/"

    def request(self, method: str, params: dict = {}) -> Response:
        endpoint = f"{self.endpoint}/{method}"
        headers = {"Authorization": f"Bearer {self.token}"}

        r = requests.get(
            endpoint,
            headers=headers,
            params=params,
        )

        if r.status_code != 200:
            raise Exception(
                f"Spacescope API returned {r.status_code} with message: {r.json()['message']}"
            )

        return r

    def get_storage_provider_power(self, storage_provider=None, date=None):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(method="storage_provider/power", params=params).json()
        return r["data"]


class DuneResource(ConfigurableResource):
    """
    Dune API resource.
    """

    DUNE_API_KEY: str = str(os.environ.get("DUNE_API_KEY"))

    def upload_csv(self, csv_file_path: str) -> requests.Response:
        """Uploads a CSV file to Dune's API.

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
