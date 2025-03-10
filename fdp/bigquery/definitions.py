import dagster as dg

from fdp.bigquery import assets_lily, assets_oso
from fdp.bigquery.resources import fdp_bigquery, lily_bigquery

assets = dg.load_assets_from_modules([assets_oso, assets_lily])

definitions = dg.Definitions(
    assets=assets,
    resources={"fdp_bigquery": fdp_bigquery, "lily_bigquery": lily_bigquery},
)
