import dagster as dg
import pyarrow as pa
from dagster_duckdb import DuckDBResource

from fdp.bigquery.resources import BigQueryArrowResource


@dg.asset(compute_kind="python")
def raw_oso_daily_filecoin_collection_events(
    context: dg.AssetExecutionContext,
    fdp_bigquery: BigQueryArrowResource,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    """
    OSO Daily Filecoin Collection Events.
    """

    query = """
        with m as (
            select
                metric_id,
                display_name
            from `opensource-observer.metrics.metrics_v0`
        )

        select
            m.display_name as event_type,
            sample_date as date,
            amount
        from `opensource-observer.metrics.timeseries_metrics_by_collection_v0` as ts
        left join m on m.metric_id = ts.metric_id
        where collection_id = 'Mo2593d20mndk7svIHlbHxKUlJZdRrKTvR0aCCVPd58='
        order by date desc, display_name desc
    """

    schema = pa.schema(
        [
            pa.field("event_type", pa.string()),
            pa.field("date", pa.date32()),
            pa.field("amount", pa.int64()),
        ]
    )

    scanner = fdp_bigquery.query_to_scanner(query, schema)  # noqa: F841

    table_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as duckdb_con:
        duckdb_con.execute(
            f"""
            create or replace table raw.{table_name} as (
                select * from scanner
            )
            """
        )

        context.log.info(f"Persisted raw.{table_name}")

    return dg.MaterializeResult()
