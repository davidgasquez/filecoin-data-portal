from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets


@dbt_assets(manifest="dbt/target/manifest.json")
def fdp_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
