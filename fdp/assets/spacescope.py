import datetime

import pandas as pd
from duckdb import CatalogException
from dagster import MaterializeResult, AssetExecutionContext, asset
from dagster_duckdb import DuckDBResource

from ..resources import SpacescopeResource

FILECOIN_FIRST_DAY = datetime.date(2020, 10, 15)


@asset(compute_kind="API")
def raw_storage_providers_daily_power(
    context: AssetExecutionContext,
    spacescope_api: SpacescopeResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Storage Providers daily power from Spacescope API.
    """

    with duckdb.get_connection() as conn:
        try:
            from_day = (
                conn.execute(
                    "select max(stat_date) as max_date from main.raw_storage_providers_daily_power"
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
                create table main.raw_storage_providers_daily_power(
                    stat_date VARCHAR,
                    miner_id VARCHAR,
                    raw_byte_power BIGINT,
                    quality_adj_power BIGINT
                );
                """
            )

        from_day = from_day + datetime.timedelta(days=1)
        from_day = from_day or FILECOIN_FIRST_DAY

        to_day = datetime.date.today() - datetime.timedelta(days=1)

        if from_day >= to_day:
            context.log.info(
                f"Storage provider power data is up to date. Last update was on {from_day}"
            )
            return MaterializeResult(
                metadata={
                    "Sample": "No new data",
                    "Rows": 0,
                }
            )

        context.log.info(
            f"Fetching storage provider power data from {from_day} to {to_day}"
        )

        df_power_data = pd.DataFrame()

        for day in pd.date_range(from_day, to_day, freq="d"):
            context.log.info(f"Fetching storage provider power data for {day}")
            power_data = spacescope_api.get_storage_provider_power(
                date=day.strftime("%Y-%m-%d"), storage_provider=None
            )
            df_power_data = pd.concat(
                [df_power_data, pd.DataFrame(power_data)], ignore_index=True
            )
            context.log.info(
                f"Fetched {len(power_data)} rows of storage provider power data for {day}"
            )

        conn.execute(
            """
            insert into main.raw_storage_providers_daily_power
            select * from df_power_data
            """
        )

        context.log.info(
            f"Persisted {df_power_data.shape[0]} rows of storage provider power data"
        )

        return MaterializeResult(
            metadata={
                "Sample": df_power_data.sample(5).to_markdown(),
                "Rows": df_power_data.shape[0],
            }
        )


@asset(compute_kind="API")
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
                    "select max(stat_date) as max_date from main.raw_storage_providers_token_balances"
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
                create table main.raw_storage_providers_token_balances (
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

        if from_day >= to_day:
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
            context.log.info(f"Fetching storage provider token balance data for {day}")
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
            insert into main.raw_storage_providers_token_balances
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


@asset(compute_kind="API")
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
                    "select max(stat_date) as max_date from main.raw_storage_providers_rewards"
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
                create table main.raw_storage_providers_rewards (
                    stat_date VARCHAR,
                    miner_id VARCHAR,
                    blocks_mined BIGINT,
                    win_count BIGINT,
                    rewards NUMERIC
                );
                """
            )

        from_day = from_day + datetime.timedelta(days=1)
        from_day = from_day or FILECOIN_FIRST_DAY

        to_day = datetime.date.today() - datetime.timedelta(days=1)

        if from_day >= to_day:
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
            context.log.info(f"Fetching storage provider rewards data for {day}")
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
            insert into main.raw_storage_providers_rewards
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
