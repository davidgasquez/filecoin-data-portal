import dagster as dg
from dagster_gcp import BigQueryResource
from dagster_duckdb import DuckDBResource


@dg.asset(compute_kind="python")
def raw_oso_daily_filecoin_collection_events(
    context: dg.AssetExecutionContext,
    fdp_bigquery: BigQueryResource,
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

    with fdp_bigquery.get_client() as client:
        job = client.query(query)
        arrow_result = job.to_arrow(create_bqstorage_client=True)

    context.log.info(f"Fetched {arrow_result.num_rows} rows from BigQuery")

    with duckdb.get_connection() as duckdb_con:
        duckdb_con.execute(
            """
            create or replace table raw.raw_oso_daily_filecoin_collection_events as (
                select * from arrow_result
            )
            """
        )

        context.log.info(f"Persisted {arrow_result.num_rows} rows")

    return dg.MaterializeResult(metadata={"dagster/row_count": arrow_result.num_rows})
