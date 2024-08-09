from dagster import AssetExecutionContext, asset
from dagster_gcp import BigQueryResource
from dagster_duckdb import DuckDBResource

from ..resources import StarboardDatabricksResource


@asset(compute_kind="python")
def raw_filecoin_state_market_deals(
    context: AssetExecutionContext,
    starboard_databricks: StarboardDatabricksResource,
    duckdb: DuckDBResource,
) -> None:
    """
    State Market Deals derived from Lily's market_deal_proposals and market_deal_states tables.
    """
    databricks_con = starboard_databricks.get_connection()
    duckdb.get_connection()

    cursor = databricks_con.cursor()
    batch_size = 2000000

    r = cursor.execute(
        """
        with market_deals as (
            select
                height,
                deal_id,
                state_root,
                piece_cid,
                padded_piece_size,
                unpadded_piece_size,
                is_verified,
                client_id,
                provider_id,
                start_epoch,
                end_epoch,
                slashed_epoch,
                storage_price_per_epoch,
                provider_collateral,
                client_collateral,
                label
            from lily.market_deal_proposals
            qualify row_number() over (partition by deal_id order by height_in_month desc, height desc) = 1
        ),

        market_chain_activity as (
            select
                deal_id,
                max(sector_start_epoch) as sector_start_epoch,
                max(slash_epoch) as slash_epoch
            from lily.market_deal_states
            group by 1
        )

        select
            d.height,
            d.deal_id,
            d.state_root,
            d.piece_cid,
            d.padded_piece_size,
            d.unpadded_piece_size,
            d.is_verified,
            d.client_id,
            d.provider_id,
            d.start_epoch,
            d.end_epoch,
            d.slashed_epoch,
            d.storage_price_per_epoch,
            d.provider_collateral,
            d.client_collateral,
            d.label,
            a.sector_start_epoch,
            a.slash_epoch
        from market_deals as d
        left join market_chain_activity as a on d.deal_id = a.deal_id
        order by d.height desc
    """
    )

    context.log.info("Fetched market deals and chain activity")

    with duckdb.get_connection() as duckdb_con:
        data = r.fetchmany_arrow(batch_size)
        duckdb_con.execute(
            """
            create or replace table raw.raw_filecoin_state_market_deals as (
                select * from data
            )
            """
        )

        context.log.info(f"Persisted {data.num_rows} rows")

        while data.num_rows > 0:
            data = r.fetchmany_arrow(batch_size)
            duckdb_con.sql(
                """
                insert into raw.raw_filecoin_state_market_deals
                select
                    *
                from data
                """
            )

            context.log.info(f"Persisted {data.num_rows} rows")


@asset(compute_kind="python")
def raw_id_addresses(
    context: AssetExecutionContext,
    lily_bigquery: BigQueryResource,
    duckdb: DuckDBResource,
) -> None:
    query = """
        select
            *
        from `lily-data.lily.id_addresses`
    """

    with lily_bigquery.get_client() as client:
        job = client.query(query)
        arrow_result = job.to_arrow(create_bqstorage_client=True)

    context.log.info(f"Fetched {arrow_result.num_rows} rows from BigQuery")

    with duckdb.get_connection() as duckdb_con:
        duckdb_con.execute(
            """
            create or replace table raw.raw_id_addresses as (
                select * from arrow_result
            )
            """
        )

        context.log.info(f"Persisted {arrow_result.num_rows} rows")


@asset(compute_kind="python")
def raw_verified_registry_verifiers(
    context: AssetExecutionContext,
    lily_bigquery: BigQueryResource,
    duckdb: DuckDBResource,
) -> None:
    query = """
        select
            *
        from `lily-data.lily.verified_registry_verifiers`
    """

    with lily_bigquery.get_client() as client:
        job = client.query(query)
        arrow_result = job.to_arrow(create_bqstorage_client=True)

    context.log.info(f"Fetched {arrow_result.num_rows} rows from BigQuery")

    with duckdb.get_connection() as duckdb_con:
        duckdb_con.execute(
            """
            create or replace table raw.raw_verified_registry_verifiers as (
                select * from arrow_result
            )
            """
        )

        context.log.info(f"Persisted {arrow_result.num_rows} rows")
