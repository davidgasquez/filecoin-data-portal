import dagster as dg

from fdp.apis import assets, fevm, goldsky, oso
from fdp.apis.resources import OsoResource
from fdp.resources import HttpClientResource

api_assets = dg.load_assets_from_modules([assets, fevm, goldsky, oso])

definitions = dg.Definitions(
    assets=api_assets,
    resources={
        "httpx_api": HttpClientResource(retries=5, timeout=45),
        "oso_api": OsoResource(OSO_API_KEY=dg.EnvVar("OSO_API_KEY")),
    },
)
