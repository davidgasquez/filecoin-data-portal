import os

from dagster import EnvVar, Definitions, load_assets_from_modules
from dagster_gcp import BigQueryResource
from dagster_duckdb import DuckDBResource
from dagster_duckdb_pandas import DuckDBPandasIOManager

from . import resources
from .assets import dbt, lily, other, datacap, reputation, spacescope

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    os.path.dirname(os.path.abspath(__file__)) + "/../data/database.duckdb",
)

all_assets = load_assets_from_modules(
    [other, datacap, lily, spacescope, reputation, dbt]
)

lily_bigquery = BigQueryResource(
    project="protocol-labs-data-nexus",
    location="us-east4",
    gcp_credentials=EnvVar("ENCODED_GOOGLE_APPLICATION_CREDENTIALS"),
)

resources = {
    "dbt": resources.dbt_resource,
    "spacescope_api": resources.SpacescopeResource(
        SPACESCOPE_TOKEN=EnvVar("SPACESCOPE_TOKEN")
    ),
    "duckdb": DuckDBResource(database=DATABASE_PATH),
    "io_manager": DuckDBPandasIOManager(database=DATABASE_PATH, schema="raw"),
    "dune": resources.DuneResource(DUNE_API_KEY=EnvVar("DUNE_API_KEY")),
    "lily_bigquery": lily_bigquery,
}

defs = Definitions(assets=[*all_assets], resources=resources)
