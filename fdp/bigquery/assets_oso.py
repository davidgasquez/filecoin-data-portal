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

    This table could be dropped at any time as it not versioned. In that case, we can swap to:

    ```sql
    select
        e.*,
        abp.artifact_source,
        abp.artifact_name,
    from `oso.timeseries_events_by_artifact_v0` e
    join `oso.artifacts_by_collection_v1` abp
    on e.to_artifact_id = abp.artifact_id
    where abp.collection_name = "filecoin-core"
    order by time desc
    ```
    """

    query = """
    select
        event_type,
        bucket_day as date,
        amount
    from `protocol-labs-data-nexus.oso.events_daily_to_collection`
    where 1=1
        and collection_id = (select collection_id from `protocol-labs-data-nexus.oso.collections_v1` where collection_name = "filecoin-core")
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
