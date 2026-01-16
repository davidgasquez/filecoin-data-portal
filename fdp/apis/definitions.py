import dagster as dg

from fdp.apis import assets, goldsky
from fdp.resources import HttpClientResource

api_assets = dg.load_assets_from_modules([assets, goldsky])

definitions = dg.Definitions(
    assets=api_assets,
    resources={
        "httpx_api": HttpClientResource(retries=5, timeout=45),
    },
)
