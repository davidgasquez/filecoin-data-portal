import dagster as dg

from fdp.dune import assets
from fdp.dune.resources import DuneResource

dune_assets = dg.load_assets_from_modules([assets])

definitions = dg.Definitions(
    assets=dune_assets,
    resources={
        "dune": DuneResource(DUNE_API_KEY=dg.EnvVar("DUNE_API_KEY")),
    },
)
