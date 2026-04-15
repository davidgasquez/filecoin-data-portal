import dagster as dg

from fdp.resources import duckdb_resource
from fdp.spacescope import assets
from fdp.spacescope.resources import SpacescopeResource

spacescope_assets = dg.load_assets_from_modules([assets])

definitions = dg.Definitions(
    assets=spacescope_assets,
    resources={
        "duckdb_spacescope": duckdb_resource,
        "spacescope_api": SpacescopeResource(
            SPACESCOPE_TOKEN=dg.EnvVar("SPACESCOPE_TOKEN")
        ),
    },
)
