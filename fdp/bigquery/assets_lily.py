import dagster as dg
import pyarrow as pa
from dagster_duckdb import DuckDBResource

from fdp.bigquery.resources import BigQueryArrowResource


@dg.asset(compute_kind="python")
def raw_id_addresses(
    context: dg.AssetExecutionContext,
    lily_bigquery: BigQueryArrowResource,
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
        _ = duckdb_con.execute(
            """
            create or replace table raw.raw_id_addresses as (
                select * from arrow_result
            )
            """
        )

        context.log.info(f"Persisted {arrow_result.num_rows} rows")


@dg.asset(compute_kind="python")
def raw_verified_registry_verifiers(
    context: dg.AssetExecutionContext,
    lily_bigquery: BigQueryArrowResource,
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
        _ = duckdb_con.execute(
            """
            create or replace table raw.raw_verified_registry_verifiers as (
                select * from arrow_result
            )
            """
        )

        context.log.info(f"Persisted {arrow_result.num_rows} rows")


@dg.asset(compute_kind="python")
def raw_daily_providers_sector_events(
    context: dg.AssetExecutionContext,
    lily_bigquery: BigQueryArrowResource,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    query = """
        with base as (
            select
                timestamp_seconds((height * 30) + 1598306400) AS timestamp,
                height,
                sector_id,
                event,
                miner_id as provider_id
            from
                `lily-data.lily.miner_sector_events`
        )

        select
            date(timestamp) as date,
            event,
            provider_id,
            approx_count_distinct(concat(cast(sector_id as string), provider_id)) as count
        from base
        group by 1, 2, 3
        order by 1 desc, 2 desc
    """

    schema: pa.Schema = pa.schema([
        pa.field("date", pa.date32()),
        pa.field("event", pa.string()),
        pa.field("provider_id", pa.string()),
        pa.field("count", pa.int64()),
    ])

    scanner = lily_bigquery.query_to_scanner(query, schema)  # noqa: F841
    table_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as duckdb_con:
        _ = duckdb_con.execute(
            f"""
            create or replace table raw.{table_name} as (
                select * from scanner
            )
            """
        )

        context.log.info(f"Persisted raw.{table_name}")

    return dg.MaterializeResult()


@dg.asset(compute_kind="python")
def raw_filecoin_state_market_deals(
    context: dg.AssetExecutionContext,
    lily_bigquery: BigQueryArrowResource,
    duckdb: DuckDBResource,
) -> None:
    # Get the max height from existing data
    with duckdb.get_connection() as duckdb_con:
        # Check if table exists and get max height
        table_exists = (
            duckdb_con.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'raw'
            AND table_name = 'raw_filecoin_state_market_deals'
        """).fetchone()[0]
            > 0
        )

        if table_exists:
            max_height_result = duckdb_con.execute("""
                SELECT COALESCE(MAX(height), 0) as max_height
                FROM raw.raw_filecoin_state_market_deals
            """).fetchone()
            max_height = max_height_result[0] if max_height_result else 0
            context.log.info(f"Found existing data with max height: {max_height}")
        else:
            max_height = 0
            context.log.info("Table does not exist, loading all data")

    # Query for new/updated deals from market_deal_proposals
    proposals_query = f"""
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
            row_number() over (
                partition by deal_id
                order by height desc
            ) as row_num
        from `lily-data.lily.market_deal_proposals`
        where height > {max_height}
    )
    select * from market_deals where row_num = 1
    """

    # Query for all deal states (we need all to capture updates)
    states_query = """
    select
        deal_id,
        max(sector_start_epoch) as sector_start_epoch,
        max(slash_epoch) as slash_epoch
    from `lily-data.lily.market_deal_states`
    group by 1
    having max(sector_start_epoch) is not null
    """

    # Execute queries
    with lily_bigquery.get_client() as client:
        # Get new proposals
        context.log.info("Fetching new deal proposals...")
        proposals_job = client.query(proposals_query)
        proposals_result = proposals_job.result()

        # Get all deal states
        context.log.info("Fetching deal states...")
        states_job = client.query(states_query)
        states_result = states_job.result()

    # Convert to Arrow tables
    proposals_sc = proposals_result.client._ensure_bqstorage_client()
    proposals_iter = proposals_result.to_arrow_iterable(
        proposals_sc, max_queue_size=500000
    )

    states_sc = states_result.client._ensure_bqstorage_client()
    states_iter = states_result.to_arrow_iterable(states_sc, max_queue_size=500000)

    # Define schemas
    proposals_schema = pa.schema([
        pa.field("height", pa.int64()),
        pa.field("deal_id", pa.string()),
        pa.field("state_root", pa.string()),
        pa.field("piece_cid", pa.string()),
        pa.field("padded_piece_size", pa.int64()),
        pa.field("unpadded_piece_size", pa.int64()),
        pa.field("is_verified", pa.bool_()),
        pa.field("client_id", pa.string()),
        pa.field("provider_id", pa.string()),
        pa.field("start_epoch", pa.int64()),
        pa.field("end_epoch", pa.int64()),
        pa.field("slashed_epoch", pa.int64()),
        pa.field("storage_price_per_epoch", pa.int64()),
        pa.field("provider_collateral", pa.int64()),
        pa.field("client_collateral", pa.int64()),
        pa.field("row_num", pa.int64()),
    ])

    states_schema = pa.schema([
        pa.field("deal_id", pa.string()),
        pa.field("sector_start_epoch", pa.int64()),
        pa.field("slash_epoch", pa.int64()),
    ])

    proposals_reader = pa.RecordBatchReader.from_batches(  # noqa: F841
        proposals_schema, proposals_iter
    )
    states_reader = pa.RecordBatchReader.from_batches(states_schema, states_iter)  # noqa: F841

    with duckdb.get_connection() as duckdb_con:
        # Create temporary tables for the new data
        duckdb_con.execute("""
            CREATE OR REPLACE TEMPORARY TABLE temp_proposals AS
            SELECT * EXCLUDE (row_num) FROM proposals_reader
        """)

        duckdb_con.execute("""
            CREATE OR REPLACE TEMPORARY TABLE temp_states AS
            SELECT * FROM states_reader
        """)

        # Join the data
        duckdb_con.execute("""
            CREATE OR REPLACE TEMPORARY TABLE temp_joined AS
            SELECT
                p.height,
                p.deal_id,
                p.state_root,
                p.piece_cid,
                p.padded_piece_size,
                p.unpadded_piece_size,
                p.is_verified,
                p.client_id,
                p.provider_id,
                p.start_epoch,
                p.end_epoch,
                p.slashed_epoch,
                p.storage_price_per_epoch,
                p.provider_collateral,
                p.client_collateral,
                s.sector_start_epoch,
                s.slash_epoch
            FROM temp_proposals p
            INNER JOIN temp_states s ON p.deal_id = s.deal_id
        """)

        # Handle incremental load
        if table_exists and max_height > 0:
            # Update existing records and insert new ones
            context.log.info("Performing incremental update...")

            # First, update existing records that might have changed states
            duckdb_con.execute("""
                UPDATE raw.raw_filecoin_state_market_deals AS target
                SET
                    sector_start_epoch = source.sector_start_epoch,
                    slash_epoch = source.slash_epoch
                FROM (
                    SELECT DISTINCT
                        existing.deal_id,
                        states.sector_start_epoch,
                        states.slash_epoch
                    FROM raw.raw_filecoin_state_market_deals AS existing
                    INNER JOIN temp_states AS states ON existing.deal_id = states.deal_id
                    WHERE existing.sector_start_epoch != states.sector_start_epoch
                       OR existing.slash_epoch != states.slash_epoch
                ) AS source
                WHERE target.deal_id = source.deal_id
            """)

            updated_count = duckdb_con.execute(
                "SELECT COUNT(*) FROM temp_joined"
            ).fetchone()[0]

            # Insert new records
            duckdb_con.execute("""
                INSERT INTO raw.raw_filecoin_state_market_deals
                SELECT * FROM temp_joined
            """)

            context.log.info(f"Inserted {updated_count} new records")
        else:
            # Create table with all data
            context.log.info("Creating table with initial data...")
            duckdb_con.execute("""
                CREATE OR REPLACE TABLE raw.raw_filecoin_state_market_deals AS
                SELECT * FROM temp_joined
                ORDER BY height DESC
            """)

            total_count = duckdb_con.execute(
                "SELECT COUNT(*) FROM raw.raw_filecoin_state_market_deals"
            ).fetchone()[0]
            context.log.info(f"Created table with {total_count} records")

        context.log.info("Persisted raw filecoin state market deals")


@dg.asset(compute_kind="python")
def raw_filecoin_transactions(
    context: dg.AssetExecutionContext,
    lily_bigquery: BigQueryArrowResource,
    duckdb: DuckDBResource,
) -> None:
    query = """
        select
            date(timestamp_seconds((height * 30) + 1598306400)) as date,
            concat(regexp_extract(actor_name, r'[^/]+$'), '/', g.method, '/', coalesce(m.method_name, 'unknown')) as method,
            sum(gas_used * pow(10, -6)) as gas_used_millions,
            count(1) as transactions,
            sum(cast(value as numeric) / 1e18) as total_value_fil
        from
            `lily-data.lily.derived_gas_outputs` as g
        left join `lily-data.lily.actor_methods` as m on g.method = m.method and regexp_extract(g.actor_name, r'[^/]+$') = m.family
        group by 1, 2
        order by 1 desc, 4 desc
    """

    with lily_bigquery.get_client() as client:
        job = client.query(query)
        arrow_result = job.to_arrow(create_bqstorage_client=True)

    context.log.info(f"Fetched {arrow_result.num_rows} rows from BigQuery")

    with duckdb.get_connection() as duckdb_con:
        _ = duckdb_con.execute(
            """
            create or replace table raw.raw_filecoin_transactions as (
                select * from arrow_result
            )
            """
        )

        context.log.info(f"Persisted {arrow_result.num_rows} rows")


@dg.asset(compute_kind="python")
def raw_filecoin_storage_providers_information(
    context: dg.AssetExecutionContext,
    lily_bigquery: BigQueryArrowResource,
    duckdb: DuckDBResource,
) -> None:
    query = """
        select
            miner_id as provider_id,
            owner_id,
            worker_id,
            peer_id,
            control_addresses,
            multi_addresses,
            sector_size / 1024 / 1024 / 1024 as sector_size_gibs
        from `lily-data.lily.miner_infos`
        qualify row_number() over (partition by miner_id order by height desc) = 1
    """

    with lily_bigquery.get_client() as client:
        job = client.query(query)
        arrow_result = job.to_arrow(create_bqstorage_client=True)

    context.log.info(f"Fetched {arrow_result.num_rows} rows from BigQuery")

    with duckdb.get_connection() as duckdb_con:
        _ = duckdb_con.execute(
            """
            create or replace table raw.raw_filecoin_storage_providers_information as (
                select * from arrow_result
            )
            """
        )

        context.log.info(f"Persisted {arrow_result.num_rows} rows")


# @dg.asset
# def raw_filecoin_sectors(
#     context: dg.AssetExecutionContext,
#     lily_bigquery: BigQueryArrowResource,
#     duckdb: DuckDBResource,
# ) -> None:
#     query = """
#         with msi as (
#             select
#                 miner_id as provider_id,
#                 sector_id,
#                 sealed_cid,
#                 height as updated_at_height,
#                 activation_epoch,
#                 expiration_epoch,
#                 deal_weight,
#                 verified_deal_weight,
#                 initial_pledge,
#                 expected_day_reward,
#                 expected_storage_pledge
#             from `lily-data.lily.miner_sector_infos_v7`

#             union all

#             select
#                 miner_id as provider_id,
#                 sector_id,
#                 sealed_cid,
#                 height as updated_at_height,
#                 activation_epoch,
#                 expiration_epoch,
#                 deal_weight,
#                 verified_deal_weight,
#                 initial_pledge,
#                 expected_day_reward,
#                 expected_storage_pledge
#             from `lily-data.lily.miner_sector_infos`
#         )
#         select
#             *
#         from msi
#         qualify row_number() over (partition by provider_id, sector_id order by updated_at_height desc) = 1
#     """

#     with lily_bigquery.get_client() as client:
#         job = client.query(query)
#         arrow_result = job.to_arrow(create_bqstorage_client=True)

#     context.log.info(f"Fetched {arrow_result.num_rows} rows from BigQuery")

#     with duckdb.get_connection() as duckdb_con:
#         _ = duckdb_con.execute(
#             """
#             create or replace table raw.raw_filecoin_sectors as (
#                 select * from arrow_result
#             )
#             """
#         )

#         context.log.info(f"Persisted {arrow_result.num_rows} rows")
