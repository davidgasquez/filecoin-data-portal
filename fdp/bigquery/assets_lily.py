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

    schema: pa.Schema = pa.schema(
        [
            pa.field("date", pa.date32()),
            pa.field("event", pa.string()),
            pa.field("provider_id", pa.string()),
            pa.field("count", pa.int64()),
        ]
    )

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
    query = """
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
                order by height desc, height desc
            ) as row_num
        from `lily-data.lily.market_deal_proposals`
    ),

    market_chain_activity as (
        select
            deal_id,
            max(sector_start_epoch) as sector_start_epoch,
            max(slash_epoch) as slash_epoch
        from `lily-data.lily.market_deal_states`
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
        a.sector_start_epoch,
        a.slash_epoch
    from market_deals as d
    left join market_chain_activity as a on d.deal_id = a.deal_id
    where 1=1
        and d.row_num = 1
        and a.sector_start_epoch is not null
    order by d.height desc
    """

    with lily_bigquery.get_client() as client:
        job = client.query(query)
        job_result = job.result()

    sc = job_result.client._ensure_bqstorage_client()
    i = job_result.to_arrow_iterable(sc, max_queue_size=500000)

    schema = pa.schema(
        [
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
            pa.field("sector_start_epoch", pa.int64()),
            pa.field("slash_epoch", pa.int64()),
        ]
    )

    reader = pa.RecordBatchReader.from_batches(schema, i)  # noqa: F841

    with duckdb.get_connection() as duckdb_con:
        _ = duckdb_con.execute(
            """
            create or replace table raw.raw_filecoin_state_market_deals as (
                select * from reader
            )
            """
        )

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


@dg.asset(compute_kind="python")
def raw_filecoin_daily_upcoming_sector_expirations(
    context: dg.AssetExecutionContext,
    lily_bigquery: BigQueryArrowResource,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    query = """
        with latest_sector_infos as (
            with msi as (
                select
                    miner_id as provider_id,
                    cast(sector_id as string) as sector_id,
                    safe_cast(height as int64) as updated_at_height,
                    safe_cast(activation_epoch as int64) as activation_epoch,
                    safe_cast(expiration_epoch as int64) as expiration_epoch,
                    coalesce(safe_cast(deal_weight as bignumeric), 0) as deal_weight,
                    coalesce(safe_cast(verified_deal_weight as bignumeric), 0) as verified_deal_weight,
                    coalesce(safe_cast(initial_pledge as bignumeric), 0) as initial_pledge,
                    coalesce(safe_cast(expected_day_reward as bignumeric), 0) as expected_day_reward,
                    coalesce(safe_cast(expected_storage_pledge as bignumeric), 0) as expected_storage_pledge
                from `lily-data.lily.miner_sector_infos_v7`

                union all

                select
                    miner_id as provider_id,
                    cast(sector_id as string) as sector_id,
                    safe_cast(height as int64) as updated_at_height,
                    safe_cast(activation_epoch as int64) as activation_epoch,
                    safe_cast(expiration_epoch as int64) as expiration_epoch,
                    coalesce(safe_cast(deal_weight as bignumeric), 0) as deal_weight,
                    coalesce(safe_cast(verified_deal_weight as bignumeric), 0) as verified_deal_weight,
                    coalesce(safe_cast(initial_pledge as bignumeric), 0) as initial_pledge,
                    coalesce(safe_cast(expected_day_reward as bignumeric), 0) as expected_day_reward,
                    coalesce(safe_cast(expected_storage_pledge as bignumeric), 0) as expected_storage_pledge
                from `lily-data.lily.miner_sector_infos`
            )

            select
                *
            from msi
            qualify row_number() over (partition by provider_id, sector_id order by updated_at_height desc) = 1
        ),

        latest_miner_infos as (
            select
                miner_id as provider_id,
                sector_size
            from `lily-data.lily.miner_infos`
            qualify row_number() over (partition by miner_id order by height desc) = 1
        ),

        upcoming_sectors as (
            select
                date(timestamp_seconds((s.expiration_epoch * 30) + 1598306400)) as expiration_date,
                cast(mi.sector_size as bignumeric) as raw_power_bytes,
                cast(mi.sector_size as bignumeric)
                + safe_divide(
                    cast(9 as bignumeric) * cast(s.verified_deal_weight as bignumeric),
                    cast(s.expiration_epoch - s.activation_epoch as bignumeric)
                ) as quality_adjusted_power_bytes,
                cast(s.initial_pledge as bignumeric) as initial_pledge_attofil,
                cast(s.expected_day_reward as bignumeric) as expected_day_reward_attofil,
                cast(s.expected_storage_pledge as bignumeric) as expected_storage_pledge_attofil,
                cast(s.deal_weight as bignumeric) as deal_weight,
                cast(s.verified_deal_weight as bignumeric) as verified_deal_weight
            from latest_sector_infos as s
            left join latest_miner_infos as mi on s.provider_id = mi.provider_id
            where 1 = 1
                and s.expiration_epoch > s.activation_epoch
                and mi.sector_size is not null
                and date(timestamp_seconds((s.expiration_epoch * 30) + 1598306400)) >= current_date()
                and date(timestamp_seconds((s.expiration_epoch * 30) + 1598306400)) <= date_add(current_date(), interval 2 year)
        ),

        daily_aggregates as (
            select
                expiration_date,
                count(*) as sector_count,
                sum(raw_power_bytes) as raw_power_bytes,
                sum(quality_adjusted_power_bytes) as quality_adjusted_power_bytes,
                sum(initial_pledge_attofil) as initial_pledge_attofil,
                sum(expected_day_reward_attofil) as expected_day_reward_attofil,
                sum(expected_storage_pledge_attofil) as expected_storage_pledge_attofil,
                sum(deal_weight) as deal_weight,
                sum(verified_deal_weight) as verified_deal_weight
            from upcoming_sectors
            group by 1
        ),

        date_calendar as (
            select
                date
            from unnest(generate_date_array(current_date(), date_add(current_date(), interval 2 year))) as date
        )

        select
            dc.date as expiration_date,
            coalesce(da.sector_count, 0) as sector_count,
            cast(coalesce(da.raw_power_bytes, 0) as string) as raw_power_bytes,
            cast(coalesce(da.quality_adjusted_power_bytes, 0) as string) as quality_adjusted_power_bytes,
            cast(coalesce(da.initial_pledge_attofil, 0) as string) as initial_pledge_attofil,
            cast(coalesce(da.expected_day_reward_attofil, 0) as string) as expected_day_reward_attofil,
            cast(coalesce(da.expected_storage_pledge_attofil, 0) as string) as expected_storage_pledge_attofil,
            cast(coalesce(da.deal_weight, 0) as string) as deal_weight,
            cast(coalesce(da.verified_deal_weight, 0) as string) as verified_deal_weight
        from date_calendar as dc
        left join daily_aggregates as da on dc.date = da.expiration_date
        order by 1
    """

    schema: pa.Schema = pa.schema(
        [
            pa.field("expiration_date", pa.date32()),
            pa.field("sector_count", pa.int64()),
            pa.field("raw_power_bytes", pa.string()),
            pa.field("quality_adjusted_power_bytes", pa.string()),
            pa.field("initial_pledge_attofil", pa.string()),
            pa.field("expected_day_reward_attofil", pa.string()),
            pa.field("expected_storage_pledge_attofil", pa.string()),
            pa.field("deal_weight", pa.string()),
            pa.field("verified_deal_weight", pa.string()),
        ]
    )

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

        row_count = duckdb_con.execute(
            f"""
            select count(*)
            from raw.{table_name}
            """
        ).fetchone()[0]

    context.log.info(f"Persisted raw.{table_name} with {row_count} rows")

    return dg.MaterializeResult(metadata={"dagster/row_count": row_count})
