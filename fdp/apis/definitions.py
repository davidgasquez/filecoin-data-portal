import dagster as dg

from fdp.apis import assets, fevm
from fdp.resources import HttpClientResource

# raw_goldsky_foc_metrics is temporarily disabled due to recurring upstream Goldsky failures.
api_assets = dg.load_assets_from_modules([assets, fevm])

definitions = dg.Definitions(
    assets=api_assets,
    resources={
        "httpx_api": HttpClientResource(retries=5, timeout=45),
    },
)
