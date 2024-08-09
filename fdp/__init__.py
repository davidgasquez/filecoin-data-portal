import os

from dagster import EnvVar, Definitions, load_assets_from_modules
from dagster_dbt import DbtProject, DbtCliResource
from dagster_duckdb import DuckDBResource
from dagster_duckdb_pandas import DuckDBPandasIOManager

from . import resources
from .assets import dbt, lily, other, datacap, reputation, spacescope

DBT_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../dbt/"
DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    os.path.dirname(os.path.abspath(__file__)) + "/../data/database.duckdb",
)

dbt_project = DbtProject(project_dir=DBT_PROJECT_DIR)
dbt_project.prepare_if_dev()
dbt_resource = DbtCliResource(project_dir=dbt_project, profiles_dir=DBT_PROJECT_DIR)

all_assets = load_assets_from_modules(
    [other, datacap, lily, spacescope, reputation, dbt]
)

resources = {
    "dbt": dbt_resource,
    "spacescope_api": resources.SpacescopeResource(
        SPACESCOPE_TOKEN=EnvVar("SPACESCOPE_TOKEN")
    ),
    "starboard_databricks": resources.StarboardDatabricksResource(
        DATABRICKS_SERVER_HOSTNAME=EnvVar("DATABRICKS_SERVER_HOSTNAME"),
        DATABRICKS_HTTP_PATH=EnvVar("DATABRICKS_HTTP_PATH"),
        DATABRICKS_ACCESS_TOKEN=EnvVar("DATABRICKS_ACCESS_TOKEN"),
    ),
    "duckdb": DuckDBResource(database=DATABASE_PATH),
    "io_manager": DuckDBPandasIOManager(database=DATABASE_PATH, schema="raw"),
    "dune": resources.DuneResource(DUNE_API_KEY=EnvVar("DUNE_API_KEY")),
}

defs = Definitions(assets=[*all_assets], resources=resources)
