import dagster as dg

from fdp.apis import assets, spark_assets
from fdp.resources import HttpClientResource

api_assets = dg.load_assets_from_modules([assets, spark_assets])

definitions = dg.Definitions(
    assets=api_assets,
    resources={
        "httpx_api": HttpClientResource(retries=5, timeout=45),
        "httpx_filspark": HttpClientResource(
            bearer_token=dg.EnvVar("SPARK_API_BEARER_TOKEN")
        ),
    },
)
