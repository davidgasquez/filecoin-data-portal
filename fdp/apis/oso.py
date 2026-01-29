import dagster as dg
from dagster_duckdb import DuckDBResource

from fdp.apis.resources import OsoResource


@dg.asset(compute_kind="python")
def raw_oso_daily_filecoin_collection_events(
    context: dg.AssetExecutionContext,
    oso_api: OsoResource,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    """
    OSO Daily Filecoin Collection Events.
    """
    df = oso_api.to_pandas(
        """
        with m as (
            select
                metric_id,
                metric_name,
                display_name
            from metrics_v0
        ),

        c as (
            select
                collection_id,
                collection_name
            from collections_v1
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
        from timeseries_metrics_by_collection_v0 as ts
        left join m on m.metric_id = ts.metric_id
        right join c on cast(c.collection_id as string) = cast(ts.collection_id as string)
        where m.metric_name like 'GITHUB_%'
        group by 1, 2, 3
        order by date desc, metric_name desc
            """
    )

    asset_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.shape[0]})
