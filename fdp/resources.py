import io
import os
import json

import pandas as pd
import requests
from dagster import ConfigurableResource
from requests import Response
from dagster_dbt import DbtProject, DbtCliResource


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

    def _extract_data(self, r: Response) -> dict:
        r_json = r.json()

        if r_json["code"] == 30004:
            return {}

        return r_json["data"]

    def get_storage_provider_power(self, storage_provider=None, date=None):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(method="storage_provider/power", params=params)

        return self._extract_data(r)

    def get_storage_provider_sector_total(self, storage_provider=None, date=None):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(method="storage_provider/sector/total", params=params)

        return self._extract_data(r)

    def get_storage_provider_sector_commits_count(
        self, storage_provider=None, date=None
    ):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(
            method="storage_provider/sector/commit_sector_count", params=params
        )

        return self._extract_data(r)

    def get_storage_provider_sector_commits_size(
        self, storage_provider=None, date=None
    ):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(
            method="storage_provider/sector/commit_sector_size", params=params
        )

        return self._extract_data(r)

    def get_storage_provider_sector_terminations(
        self, storage_provider=None, date=None
    ):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(method="storage_provider/sector/terminate", params=params)

        return self._extract_data(r)

    def get_storage_provider_sector_faults(self, storage_provider=None, date=None):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(method="storage_provider/sector/fault", params=params)

        return self._extract_data(r)

    def get_storage_provider_sector_recoveries(self, storage_provider=None, date=None):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(method="storage_provider/sector/recover", params=params)

        return self._extract_data(r)

    def get_storage_provider_sector_expirations(self, storage_provider=None, date=None):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(method="storage_provider/sector/expire", params=params)

        return self._extract_data(r)

    def get_storage_provider_sector_extensions(self, storage_provider=None, date=None):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(method="storage_provider/sector/extend", params=params)

        return self._extract_data(r)

    def get_storage_provider_sector_snaps(self, storage_provider=None, date=None):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(method="storage_provider/sector/snap", params=params)
        return self._extract_data(r)

    def get_storage_provider_sector_durations(self, storage_provider=None, date=None):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(
            method="storage_provider/sector/sector_duration", params=params
        )
        return self._extract_data(r)

    def get_storage_provider_token_balance(self, storage_provider=None, date=None):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(method="storage_provider/token_balance", params=params)

        return self._extract_data(r)

    def get_storage_provider_rewards(self, storage_provider=None, date=None):
        params = {"state_date": date, "miner_id": storage_provider}
        r = self.request(method="storage_provider/rewards", params=params)

        return self._extract_data(r)

    def get_network_user_address_count(self, start_date=None, end_date=None):
        params = {"start_date": start_date, "end_date": end_date}
        r = self.request(method="network_user/address_count", params=params)

        return self._extract_data(r)

    def get_network_base_fee(self, start_hour=None, end_hour=None):
        params = {"start_hour": start_hour, "end_hour": end_hour}
        r = self.request(method="gas/network_base_fee", params=params)

        return self._extract_data(r)

    def get_circulating_supply(self, start_date=None, end_date=None):
        params = {"start_date": start_date, "end_date": end_date}
        r = self.request(method="circulating_supply/circulating_supply", params=params)

        return self._extract_data(r)

    def get_block_rewards(self, start_date=None, end_date=None):
        params = {"start_date": start_date, "end_date": end_date}
        r = self.request(method="/economics/block_reward", params=params)

        return self._extract_data(r)

    def get_storage_provider_basic_info(self, miner_id=None):
        params = {"miner_id": miner_id}
        r = self.request(method="/storage_provider/basic_info", params=params)

        return self._extract_data(r)

    def get_storage_provider_deal_count(self, miner_id=None, state_date=None):
        params = {"miner_id": miner_id, "state_date": state_date}
        r = self.request(method="/storage_provider/deals/deal_count", params=params)

        return self._extract_data(r)

    def get_storage_provider_deal_duration(self, miner_id=None, state_date=None):
        params = {"miner_id": miner_id, "state_date": state_date}
        r = self.request(method="/storage_provider/deals/deal_duration", params=params)

        return self._extract_data(r)

    def get_storage_provider_deal_revenue(self, miner_id=None, state_date=None):
        params = {"miner_id": miner_id, "state_date": state_date}
        r = self.request(method="/storage_provider/deals/deal_revenue", params=params)

        return self._extract_data(r)


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

        headers = {
            "X-Dune-Api-Key": self.DUNE_API_KEY,
            "Content-Type": "application/json",
        }

        payload = {
            "table_name": name,
            "is_private": False,
            "data": df_csv,
        }

        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()

        return response


DBT_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../dbt/"
DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    os.path.dirname(os.path.abspath(__file__)) + "/../data/database.duckdb",
)

dbt_project = DbtProject(project_dir=DBT_PROJECT_DIR)
dbt_project.prepare_if_dev()
dbt_resource = DbtCliResource(project_dir=dbt_project, profiles_dir=DBT_PROJECT_DIR)
