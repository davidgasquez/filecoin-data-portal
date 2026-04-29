# asset.description = Daily public goods funding deployments from OSO.

# asset.materialization = dataframe

# asset.column = date | UTC disbursement date.
# asset.column = deployment_id | Stable deployment identifier.
# asset.column = program | Public goods funding program.
# asset.column = name | Deployment name.
# asset.column = disbursed_usd | Amount disbursed on the date, in USD.

# asset.not_null = date
# asset.not_null = deployment_id
# asset.not_null = program
# asset.not_null = name
# asset.not_null = disbursed_usd
# asset.assert = disbursed_usd >= 0

import os

import polars as pl
from pyoso import Client

QUERY = """
select
    bucket_day as date,
    lower(
        regexp_replace(
            concat(event_source, '_', coalesce(tag, 'untagged')),
            '[^A-Za-z0-9]+',
            '_'
        )
    ) as deployment_id,
    event_source as program,
    coalesce(tag, event_source) as name,
    sum(amount) as disbursed_usd
from filecoin.roi.all_funding_events
where currency = 'USD'
  and amount is not null
  and event_source in ('PROPGF', 'RETROPGF')
group by 1, 2, 3, 4
order by date desc, deployment_id
"""


def pgf_deployments() -> pl.DataFrame:
    if not os.environ.get("OSO_API_KEY"):
        raise RuntimeError("OSO_API_KEY is required to fetch PGF deployments")

    rows = Client().query(QUERY).data.data
    return pl.DataFrame(
        rows,
        schema={
            "date": pl.String,
            "deployment_id": pl.String,
            "program": pl.String,
            "name": pl.String,
            "disbursed_usd": pl.Float64,
        },
        orient="row",
    ).with_columns(pl.col("date").str.to_date())
