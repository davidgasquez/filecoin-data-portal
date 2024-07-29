import datetime

import pandas as pd
from duckdb import CatalogException
from dagster import (
    Backoff,
    RetryPolicy,
    MaterializeResult,
    AssetExecutionContext,
    asset,
)
from dagster_duckdb import DuckDBResource

from ..resources import SpacescopeResource

FILECOIN_FIRST_DAY = datetime.date(2020, 10, 15)


def fetch_and_persist_data(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
    table_name: str,
    api_call,
    create_table_query,
) -> MaterializeResult:
    """
    Fetches data from Spacescope API and persists it in DuckDB.
    """
    with duckdb.get_connection() as conn:
        try:
            from_day = conn.execute(
                f"""
                select
                    max(stat_date) as max_date
                from raw.{table_name}
                """
            ).fetchone()[0]  # type: ignore

            if from_day:
                from_day = pd.to_datetime(
                    from_day).date() + datetime.timedelta(days=1)
        except CatalogException:
            from_day = FILECOIN_FIRST_DAY
            conn.execute(create_table_query)

        from_day = from_day or FILECOIN_FIRST_DAY
        to_day = datetime.date.today() - datetime.timedelta(days=1)

        if from_day > to_day:
            context.log.info(
                f"Data is up to date. Last update was on {from_day}")
            return MaterializeResult()

        context.log.info(f"Fetching data from {from_day} to {to_day}")

        df = pd.DataFrame()

        for day in pd.date_range(from_day, to_day, freq="d"):
            context.log.info(f"Fetching data for {day}")
            day_df = api_call(date=day.strftime(
                "%Y-%m-%d"), storage_provider=None)
            df = pd.concat([df, pd.DataFrame(day_df)], ignore_index=True)
            context.log.info(f"Fetched {len(day_df)} rows for {day}")

        conn.execute(
            f"""
            insert into raw.{table_name}
            select * from df
            """
        )

        context.log.info(f"Persisted {df.shape[0]} rows")

        return MaterializeResult()


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_storage_providers_daily_power(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Storage Providers daily power from Spacescope API.
    """

    table_name = context.asset_key.to_user_string()

    create_table_query = f"""
        create table raw.{table_name}(
            stat_date VARCHAR,
            miner_id VARCHAR,
            raw_byte_power BIGINT,
            quality_adj_power BIGINT
        );
    """

    return fetch_and_persist_data(
        context,
        duckdb,
        table_name,
        spacescope_api.get_storage_provider_power,
        create_table_query,
    )


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_storage_providers_token_balances(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Storage Providers token balance from Spacescope API.
    """

    with duckdb.get_connection() as conn:
        try:
            from_day = (
                conn.execute(
                    "select max(stat_date) as max_date from raw.raw_storage_providers_token_balances"
                )
                .df()["max_date"]
                .values[0]
            )
            if from_day:
                from_day = pd.to_datetime(from_day).date()
        except CatalogException:
            from_day = FILECOIN_FIRST_DAY

            conn.execute(
                """
                create table raw.raw_storage_providers_token_balances (
                    stat_date VARCHAR,
                    miner_id VARCHAR,
                    balance NUMERIC,
                    initial_pledge NUMERIC,
                    locked_funds NUMERIC,
                    pre_commit_deposits NUMERIC,
                    provider_collateral NUMERIC,
                    fee_debt NUMERIC
                );
                """
            )

        from_day = from_day + datetime.timedelta(days=1)
        from_day = from_day or FILECOIN_FIRST_DAY

        to_day = datetime.date.today() - datetime.timedelta(days=1)

        if from_day > to_day:
            context.log.info(
                f"Storage provider token balance data is up to date. Last update was on {from_day}"
            )
            return MaterializeResult(
                metadata={
                    "Sample": "No new data",
                    "Rows": 0,
                }
            )

        context.log.info(
            f"Fetching storage provider token balance data from {from_day} to {to_day}"
        )

        df_token_balance_data = pd.DataFrame()

        for day in pd.date_range(from_day, to_day, freq="d"):
            context.log.info(
                f"Fetching storage provider token balance data for {day}")
            token_balance_data = spacescope_api.get_storage_provider_token_balance(
                date=day.strftime("%Y-%m-%d"), storage_provider=None
            )
            df_token_balance_data = pd.concat(
                [df_token_balance_data, pd.DataFrame(token_balance_data)],
                ignore_index=True,
            )
            context.log.info(
                f"Fetched {len(token_balance_data)} rows of storage provider token balance data for {day}"
            )

        conn.execute(
            """
            insert into raw.raw_storage_providers_token_balances
            select * from df_token_balance_data
            """
        )

        context.log.info(
            f"Persisted {df_token_balance_data.shape[0]} rows of storage provider token balance data"
        )

        return MaterializeResult(
            metadata={
                "Sample": df_token_balance_data.sample(5).to_markdown(),
                "Rows": df_token_balance_data.shape[0],
            }
        )


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_storage_providers_rewards(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Storage Providers rewards from Spacescope API.
    """

    with duckdb.get_connection() as conn:
        try:
            from_day = (
                conn.execute(
                    "select max(stat_date) as max_date from raw.raw_storage_providers_rewards"
                )
                .df()["max_date"]
                .values[0]
            )

            if from_day:
                from_day = pd.to_datetime(from_day).date()
            else:
                from_day = FILECOIN_FIRST_DAY

        except CatalogException:
            from_day = FILECOIN_FIRST_DAY

            conn.execute(
                """
                create table raw.raw_storage_providers_rewards (
                    stat_date VARCHAR,
                    miner_id VARCHAR,
                    blocks_mined BIGINT,
                    win_count BIGINT,
                    rewards NUMERIC
                );
                """
            )

        context.log.info(f"Last update was on {from_day}")

        from_day = from_day + datetime.timedelta(days=1)
        from_day = from_day or FILECOIN_FIRST_DAY

        to_day = datetime.date.today() - datetime.timedelta(days=1)

        if from_day > to_day:
            context.log.info(
                f"Storage provider rewards data is up to date. Last update was on {from_day}"
            )
            return MaterializeResult(
                metadata={
                    "Sample": "No new data",
                    "Rows": 0,
                }
            )

        context.log.info(
            f"Fetching storage provider rewards data from {from_day} to {to_day}"
        )

        df_rewards_data = pd.DataFrame()

        for day in pd.date_range(from_day, to_day, freq="d"):
            context.log.info(
                f"Fetching storage provider rewards data for {day}")
            rewards_data = spacescope_api.get_storage_provider_rewards(
                date=day.strftime("%Y-%m-%d"), storage_provider=None
            )
            df_rewards_data = pd.concat(
                [df_rewards_data, pd.DataFrame(rewards_data)],
                ignore_index=True,
            )
            context.log.info(
                f"Fetched {len(rewards_data)} rows of storage provider rewards data for {day}"
            )

        conn.execute(
            """
            insert into raw.raw_storage_providers_rewards
            select * from df_rewards_data
            """
        )

        context.log.info(
            f"Persisted {df_rewards_data.shape[0]} rows of storage provider rewards data"
        )

        return MaterializeResult(
            metadata={
                "Sample": df_rewards_data.sample(5).to_markdown(),
                "Rows": df_rewards_data.shape[0],
            }
        )


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_storage_providers_sector_totals(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    The cumulative number of sectors and daily onboarded sectors of the storage providers.
    """

    table_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as conn:
        try:
            from_day = conn.execute(
                f"select max(stat_date) as max_date from raw.{table_name}"
            ).fetchone()[0]  # type: ignore

            if from_day:
                from_day = pd.to_datetime(
                    from_day).date() + datetime.timedelta(days=1)
        except CatalogException:
            from_day = FILECOIN_FIRST_DAY
            conn.execute(
                f"""
                create table raw.{table_name}(
                    stat_date VARCHAR,
                    miner_id VARCHAR,
                    total_num_sector BIGINT,
                    total_sector_rbp BIGINT,
                    total_sector_qap BIGINT,
                    daily_sector_onboarding_count BIGINT,
                    daily_sector_onboarding_rbp BIGINT,
                    daily_sector_onboarding_qap BIGINT
                );
                """
            )

        from_day = from_day or FILECOIN_FIRST_DAY

        to_day = datetime.date.today() - datetime.timedelta(days=1)

        if from_day > to_day:
            context.log.info(
                f"Data is up to date. Last update was on {from_day}")
            return MaterializeResult()

        context.log.info(f"Fetching data from {from_day} to {to_day}")

        df = pd.DataFrame()

        for day in pd.date_range(from_day, to_day, freq="d"):
            context.log.info(f"Fetching data for {day}")
            day_df = spacescope_api.get_storage_provider_sector_total(
                date=day.strftime("%Y-%m-%d"), storage_provider=None
            )
            df = pd.concat([df, pd.DataFrame(day_df)], ignore_index=True)
            context.log.info(f"Fetched {len(day_df)} rows for {day}")

        conn.execute(
            f"""
            insert into raw.{table_name}
            select * from df
            """
        )

        context.log.info(f"Persisted {df.shape[0]} rows")

        return MaterializeResult()


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_storage_providers_sector_terminations(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    The statistics of sector termination of the storage providers.
    """

    table_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as conn:
        try:
            from_day = conn.execute(
                f"select max(stat_date) as max_date from raw.{table_name}"
            ).fetchone()[0]  # type: ignore

            if from_day:
                from_day = pd.to_datetime(
                    from_day).date() + datetime.timedelta(days=1)
        except CatalogException:
            from_day = FILECOIN_FIRST_DAY
            conn.execute(
                f"""
                create table raw.{table_name}(
                    stat_date VARCHAR,
                    miner_id VARCHAR,
                    daily_new_terminate_rbp BIGINT,
                    daily_new_terminate_qap BIGINT,
                    total_terminate_rbp DOUBLE,
                    total_terminate_qap DOUBLE,
                    daily_new_active_terminate_rbp DOUBLE,
                    daily_new_active_terminate_qap DOUBLE,
                    total_active_terminate_rbp DOUBLE,
                    total_active_terminate_qap DOUBLE,
                    daily_new_passive_terminate_rbp DOUBLE,
                    daily_new_passive_terminate_qap DOUBLE,
                    total_passive_terminate_rbp DOUBLE,
                    total_passive_terminate_qap DOUBLE,
                );
                """
            )

        from_day = from_day or FILECOIN_FIRST_DAY

        to_day = datetime.date.today() - datetime.timedelta(days=1)

        if from_day > to_day:
            context.log.info(
                f"Data is up to date. Last update was on {from_day}")
            return MaterializeResult()

        context.log.info(f"Fetching data from {from_day} to {to_day}")

        df = pd.DataFrame()

        for day in pd.date_range(from_day, to_day, freq="d"):
            context.log.info(f"Fetching data for {day}")
            day_df = spacescope_api.get_storage_provider_sector_terminations(
                date=day.strftime("%Y-%m-%d"), storage_provider=None
            )
            df = pd.concat([df, pd.DataFrame(day_df)], ignore_index=True)
            context.log.info(f"Fetched {len(day_df)} rows for {day}")

        conn.execute(
            f"""
            insert into raw.{table_name}
            select * from df
            """
        )

        context.log.info(f"Persisted {df.shape[0]} rows")

        return MaterializeResult()


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_storage_providers_sector_faults(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    The statistics of sector faulted of the storage providers.
    """

    table_name = context.asset_key.to_user_string()

    create_table_query = f"""
        create table raw.{table_name}(
            stat_date VARCHAR,
            miner_id VARCHAR,
            daily_new_fault_rbp BIGINT,
            daily_new_fault_qap BIGINT,
            active_fault_rbp DOUBLE,
            active_fault_qap DOUBLE,
        );
    """

    return fetch_and_persist_data(
        context,
        duckdb,
        table_name,
        spacescope_api.get_storage_provider_sector_faults,
        create_table_query,
    )


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_storage_providers_sector_recoveries(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    The statistics of sector recovered of the storage providers.
    """

    table_name = context.asset_key.to_user_string()

    create_table_query = f"""
        create table raw.{table_name}(
            stat_date VARCHAR,
            miner_id VARCHAR,
            daily_new_recover_rbp BIGINT,
            daily_new_recover_qap BIGINT
        );
    """

    return fetch_and_persist_data(
        context,
        duckdb,
        table_name,
        spacescope_api.get_storage_provider_sector_recoveries,
        create_table_query,
    )


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_storage_providers_sector_expirations(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    The statistics of sector recovered of the storage providers.
    """

    table_name = context.asset_key.to_user_string()

    create_table_query = f"""
        create table raw.{table_name}(
            stat_date VARCHAR,
            miner_id VARCHAR,
            daily_new_expire_rbp BIGINT,
            daily_new_expire_qap BIGINT,
            total_expire_rbp BIGINT,
            total_expire_qap BIGINT
        );
    """

    return fetch_and_persist_data(
        context,
        duckdb,
        table_name,
        spacescope_api.get_storage_provider_sector_expirations,
        create_table_query,
    )


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_storage_providers_sector_extensions(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    The statistics of sector recovered of the storage providers.
    """

    table_name = context.asset_key.to_user_string()

    create_table_query = f"""
        create table raw.{table_name}(
            stat_date VARCHAR,
            miner_id VARCHAR,
            daily_new_extend_rbp BIGINT,
            daily_new_extend_qap BIGINT,
        );
    """

    return fetch_and_persist_data(
        context,
        duckdb,
        table_name,
        spacescope_api.get_storage_provider_sector_extensions,
        create_table_query,
    )


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_storage_providers_sector_snaps(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    The statistics of sector recovered of the storage providers.
    """

    table_name = context.asset_key.to_user_string()

    create_table_query = f"""
        create table raw.{table_name}(
            stat_date VARCHAR,
            miner_id VARCHAR,
            daily_new_snap_rbp BIGINT,
            daily_new_snap_qap BIGINT,
            total_snap_rbp BIGINT,
            total_snap_qap BIGINT,
        );
    """

    return fetch_and_persist_data(
        context,
        duckdb,
        table_name,
        spacescope_api.get_storage_provider_sector_snaps,
        create_table_query,
    )


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_storage_providers_sector_durations(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    The statistics of sector recovered of the storage providers.
    """

    table_name = context.asset_key.to_user_string()

    create_table_query = f"""
        create table raw.{table_name}(
            stat_date VARCHAR,
            miner_id VARCHAR,
            avg_active_sector_duration_days INT,
            std_active_sector_duration_days INT,
        );
    """

    return fetch_and_persist_data(
        context,
        duckdb,
        table_name,
        spacescope_api.get_storage_provider_sector_durations,
        create_table_query,
    )


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_storage_providers_sector_commits_count(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    The cumulative number of sector onboarded on the Filecoin Network of the storage providers.
    """

    table_name = context.asset_key.to_user_string()

    create_table_query = f"""
        create table raw.{table_name}(
            stat_date VARCHAR,
            miner_id VARCHAR,
            total_sealed_sector_count BIGINT,
            precommit_sector_count BIGINT,
            precommit_batch_sector_count BIGINT,
            avg_precommit_batch_sector_count BIGINT,
            provecommit_sector_count BIGINT,
            provecommit_batch_sector_count BIGINT,
            avg_provecommit_batch_sector_count BIGINT,
        );
    """

    return fetch_and_persist_data(
        context,
        duckdb,
        table_name,
        spacescope_api.get_storage_provider_sector_commits_count,
        create_table_query,
    )


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_storage_providers_sector_commits_size(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    The cumulative size of sector onboarded on the Filecoin Network of the storage providers.
    """

    table_name = context.asset_key.to_user_string()

    create_table_query = f"""
        create table raw.{table_name}(
            stat_date VARCHAR,
            miner_id VARCHAR,
            precommit_sector_rbp BIGINT,
            precommit_sector_qap BIGINT,
            precommit_batch_sector_rbp BIGINT,
            precommit_batch_sector_qap BIGINT,
            provecommit_sector_rbp BIGINT,
            provecommit_sector_qap BIGINT,
            provecommit_batch_sector_rbp BIGINT,
        );
    """

    return fetch_and_persist_data(
        context,
        duckdb,
        table_name,
        spacescope_api.get_storage_provider_sector_commits_count,
        create_table_query,
    )


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_network_user_address_count(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    The cumulative count of unique addresses interacting with the Filecoin Network.
    """

    table_name = context.asset_key.to_user_string()

    from_day = FILECOIN_FIRST_DAY
    to_day = datetime.date.today() - datetime.timedelta(days=1)

    context.log.info(f"Fetching data from {from_day} to {to_day}")

    df = pd.DataFrame()

    current_start_day = from_day
    while current_start_day <= to_day:
        current_end_day = min(current_start_day +
                              datetime.timedelta(days=89), to_day)
        context.log.info(
            f"Fetching data from {current_start_day} to {current_end_day}")

        batch_df = spacescope_api.get_network_user_address_count(
            start_date=current_start_day.strftime("%Y-%m-%d"),
            end_date=current_end_day.strftime("%Y-%m-%d"),
        )
        df = pd.concat([df, pd.DataFrame(batch_df)], ignore_index=True)
        context.log.info(
            f"Fetched {len(batch_df)} rows from {current_start_day} to {current_end_day}"
        )

        current_start_day = current_end_day + datetime.timedelta(days=1)

    with duckdb.get_connection() as conn:
        conn.execute(
            f"""
            create or replace table raw.{table_name} as (
                select * from df
            )
            """
        )

    context.log.info(f"Persisted {df.shape[0]} rows")

    return MaterializeResult()


@asset(
    compute_kind="API",
    retry_policy=RetryPolicy(max_retries=3, delay=20,
                             backoff=Backoff.EXPONENTIAL),
)
def raw_network_base_fee(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    The base fee required to send a message to the Filecoin Network.
    """

    table_name = context.asset_key.to_user_string()

    from_day = FILECOIN_FIRST_DAY
    to_day = datetime.date.today() - datetime.timedelta(days=1)

    context.log.info(f"Fetching data from {from_day} to {to_day}")

    df = pd.DataFrame()

    current_start_day = from_day
    while current_start_day <= to_day:
        current_end_day = min(current_start_day +
                              datetime.timedelta(days=30), to_day)
        context.log.info(
            f"Fetching data from {current_start_day} to {current_end_day}")

        batch_df = spacescope_api.get_network_base_fee(
            start_hour=current_start_day.strftime("%Y-%m-%dT%H:%M:%SZ"),
            end_hour=current_end_day.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        df = pd.concat([df, pd.DataFrame(batch_df)], ignore_index=True)
        context.log.info(
            f"Fetched {len(batch_df)} rows from {current_start_day} to {current_end_day}"
        )

        current_start_day = current_end_day + datetime.timedelta(days=1)

    with duckdb.get_connection() as conn:
        conn.execute(
            f"""
            create or replace table raw.{table_name} as (
                select * from df
            )
            """
        )

    context.log.info(f"Persisted {df.shape[0]} rows")

    return MaterializeResult()
