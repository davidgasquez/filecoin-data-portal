import os

import requests
from dagster import ConfigurableResource
from requests import Response


class SpacescopeResource(ConfigurableResource):
    """
    Spacescope API resource.
    """

    token = os.getenv(("SPACESCOPE_TOKEN"))
    endpoint = "https://api.spacescope.io/v2/"

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
