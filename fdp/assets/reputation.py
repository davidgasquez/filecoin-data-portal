import datetime

import pandas as pd
import requests
from dagster import (
    Output,
    MetadataValue,
    MaterializeResult,
    AssetExecutionContext,
    asset,
)
from dagster_duckdb import DuckDBResource


@asset(compute_kind="python")
def raw_storage_providers_filrep_reputation(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Storage Provider reputation data from Filrep (https://filrep.io).
    """

    url = "https://api.filrep.io/api/v1/miners"

    r = requests.get(url)

    try:
        storage_providers = pd.DataFrame(r.json()["miners"])
    except Exception:
        context.log.error(f"Error fetching data from {url}. Reason: {r.reason}")
        return MaterializeResult()

    table_name = context.asset_key.to_user_string()

    context.log.info(f"Creating table {table_name}")

    query = f"""
    create or replace table raw.{table_name} as (
        select
            *
        from storage_providers
    );
    """

    storage_providers["name"] = storage_providers["tag"].apply(lambda x: x.get("name"))
    storage_providers = storage_providers.convert_dtypes()
    storage_providers = storage_providers.drop(
        columns=[
            "id",
            "price",
            "verifiedPrice",
            "minPieceSize",
            "maxPieceSize",
            "rawPower",
            "qualityAdjPower",
            "creditScore",
        ]
    )

    with duckdb.get_connection() as conn:
        conn.execute(query)

    return MaterializeResult()


@asset(compute_kind="python")
def raw_spark_retrieval_success_rate(
    context: AssetExecutionContext,
) -> Output[pd.DataFrame]:
    """
    Spark retrieval success rate.
    """
    first_day = datetime.date(2024, 4, 1)
    today = datetime.date.today()

    df = pd.DataFrame()

    for day in pd.date_range(first_day, today, freq="d"):
        context.log.info(f"Fetching retrieval success rate data for {day}")
        date = day.strftime("%Y-%m-%d")
        url = "https://stats.filspark.com/miners/retrieval-success-rate/summary"
        url = f"{url}?from={date}&to={date}"

        date_df = pd.DataFrame(requests.get(url).json())
        date_df["date"] = day
        df = pd.concat([df, date_df], ignore_index=True)

    df.rename(columns={"miner_id": "provider_id"}, inplace=True)

    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})
