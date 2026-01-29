import dagster as dg
import pandas as pd
from pydantic import PrivateAttr
from pyoso import Client


class OsoResource(dg.ConfigurableResource):
    """
    OSO API resource.
    """

    OSO_API_KEY: str

    _client: Client = PrivateAttr()

    def setup_for_execution(self, context: dg.InitResourceContext) -> None:
        self._client = Client(api_key=self.OSO_API_KEY)

    def to_pandas(self, query: str) -> pd.DataFrame:
        return self._client.to_pandas(query)
