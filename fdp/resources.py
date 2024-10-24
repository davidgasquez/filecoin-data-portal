import os

import httpx
import dagster as dg
from pydantic import PrivateAttr
from dagster_duckdb import DuckDBResource
from dagster_duckdb_pandas import DuckDBPandasIOManager

DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/database.duckdb")

duckdb_resource = DuckDBResource(database=DATABASE_PATH)
duckdb_io_manager = DuckDBPandasIOManager(database=DATABASE_PATH, schema="raw")


class HttpClientResource(dg.ConfigurableResource):
    """
    HTTP client resource.
    """

    retries: int = 3
    verify: bool = False
    timeout: int = 30
    follow_redirects: bool = True
    bearer_token: str = ""

    _client: httpx.Client = PrivateAttr()

    def setup_for_execution(self, context: dg.InitResourceContext) -> None:
        transport = httpx.HTTPTransport(retries=self.retries, verify=self.verify)

        self._client = httpx.Client(
            transport=transport,
            timeout=self.timeout,
            follow_redirects=self.follow_redirects,
            headers={"Authorization": f"Bearer {self.bearer_token}"}
            if self.bearer_token
            else {},
        )

    def get(self, url: str, **kwargs) -> httpx.Response:
        return self._client.get(url, **kwargs)
