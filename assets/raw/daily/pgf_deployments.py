# asset.description = Daily public goods funding deployments from OSO.
# https://raw.githubusercontent.com/opensource-observer/insights/refs/heads/main/community/filecoin/skills.md

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
    sample_date as date,
    lower(
        regexp_replace(
            concat(
                case
                    when metric_name = 'propgf_amount_usd_equiv' then 'propgf'
                    when metric_name = 'retropgf_amount_usd_equiv' then 'retropgf'
                end,
                '_',
                oso_project_slug
            ),
            '[^A-Za-z0-9]+',
            '_'
        )
    ) as deployment_id,
    case
        when metric_name = 'propgf_amount_usd_equiv' then 'PROPGF'
        when metric_name = 'retropgf_amount_usd_equiv' then 'RETROPGF'
    end as program,
    oso_project_slug as name,
    sum(amount) as disbursed_usd
from filecoin.filpgf_public.timeseries_metrics_by_project
where time_interval = 'daily'
  and metric_name in (
    'propgf_amount_usd_equiv',
    'retropgf_amount_usd_equiv'
  )
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
