import dagster as dg

from fdp.dbt import assets
from fdp.dbt.resources import dbt_resource

aemet_assets = dg.load_assets_from_modules([assets])

definitions = dg.Definitions(assets=aemet_assets, resources={"dbt": dbt_resource})
