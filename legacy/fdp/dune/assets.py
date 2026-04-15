import dagster as dg
from dagster_duckdb import DuckDBResource

from fdp.dune.resources import DuneResource


@dg.asset(compute_kind="API", deps=["filecoin_daily_metrics"])
def dune_metrics(dune: DuneResource, duckdb: DuckDBResource) -> None:
    """
    Uploads filecoin daily metrics to Dune.
    """

    with duckdb.get_connection() as conn:
        filecoin_daily_metrics = conn.execute("""
            select
                *
            from filecoin_daily_metrics
            where date > '2021-01-01'
        """).df()

    dune.upload_df(filecoin_daily_metrics, "filecoin_daily_metrics")
