import io
import json

import pandas as pd
import dagster as dg
import requests


class DuneResource(dg.ConfigurableResource):
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
