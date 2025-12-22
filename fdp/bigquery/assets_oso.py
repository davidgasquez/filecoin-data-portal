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
                metric_name,
                display_name
            from `opensource-observer.oso.metrics_v0`
        ),

        c as (
            select
                collection_id,
                collection_name
            from `opensource-observer.oso.collections_v1`
            where collection_name in (
                'filecoin-foundation',
                'filecoin-core'
            )
        )

        select
            m.metric_name as event_type,
            m.display_name as event_display_name,
            cast(sample_date as date) as date,
            sum(safe_cast(amount as int64)) as amount
        from `opensource-observer.oso.timeseries_metrics_by_collection_v0` as ts
        left join m on m.metric_id = ts.metric_id
        right join c on cast(c.collection_id as string) = cast(ts.collection_id as string)
        where m.metric_name like 'GITHUB_%'
        group by 1, 2, 3
        order by date desc, metric_name desc
    """

    schema = pa.schema(
        [
            pa.field("event_type", pa.string()),
            pa.field("event_display_name", pa.string()),
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
