import dagster as dg

from fdp.datacapstats import assets
from fdp.resources import HttpClientResource, duckdb_resource

datacapstats_assets = dg.load_assets_from_modules([assets])

definitions = dg.Definitions(
    assets=datacapstats_assets,
    resources={
        "duckdb_datacapstats": duckdb_resource,
        "httpx_datacapstats": HttpClientResource(
            bearer_token=dg.EnvVar("GITHUB_TOKEN")
        ),
    },
)
