import os

from dagster import Definitions, load_assets_from_modules
from dagster_dbt import dbt_cli_resource, load_assets_from_dbt_project
from dagster_duckdb import DuckDBResource
from dagster_duckdb_pandas import DuckDBPandasIOManager

from . import assets, resources

DBT_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../dbt/"
DATA_DIR = os.getenv("DATA_DIR", "/workspaces/filecoin-data-portal/data/")

dbt_resource = dbt_cli_resource.configured(
    {"project_dir": DBT_PROJECT_DIR, "profiles_dir": DBT_PROJECT_DIR}
)

dbt_assets = load_assets_from_dbt_project(DBT_PROJECT_DIR, DBT_PROJECT_DIR)
all_assets = load_assets_from_modules([assets])

resources = {
    "dbt": dbt_resource,
    "spacescope_api": resources.SpacescopeResource(),
    "duckdb": DuckDBResource(database=DATA_DIR + "local.duckdb"),
    "io_manager": DuckDBPandasIOManager(
        database=DATA_DIR + "local.duckdb",
    ),
}

defs = Definitions(assets=[*dbt_assets, *all_assets], resources=resources)
