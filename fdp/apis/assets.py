import datetime

import pandas as pd
import dagster as dg
import requests
from dagster_duckdb import DuckDBResource

from fdp.resources import HttpClientResource


@dg.asset(compute_kind="python")
def raw_storage_providers_location_provider_quest(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    """
    Storage Providers location information from Provider Quest (https://provider.quest).

    Synthetic locations documentation: https://observablehq.com/@jimpick/provider-quest-synthetic-locations
    """
    url = "https://provider-quest.s3.us-west-2.amazonaws.com/dist/geoip-lookups/synthetic-locations-latest.json"
    all_df = pd.read_json(url, typ="series")
    df = pd.json_normalize(all_df["providerLocations"])

    asset_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.shape[0]})


@dg.asset(compute_kind="python")
def raw_storage_providers_evp_outputs(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    """
    Storage Providers Retrieves all existing Energy Validation Process outputs.
    """
    r = requests.get("https://sp-outputs-api.vercel.app/api/evp-outputs", verify=False)
    r.raise_for_status()

    df = pd.DataFrame(r.json()["data"])

    asset_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.shape[0]})


@dg.asset(compute_kind="python")
def raw_storage_providers_energy_name_mapping(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
    raw_storage_providers_evp_outputs: pd.DataFrame,
) -> dg.MaterializeResult:
    """
    Storage Providers Entities Mapping to Provider IDs.
    """
    raw_storage_providers_evp_outputs["provider_id"] = (
        raw_storage_providers_evp_outputs["miner_ids"].str.split(",")
    )

    df = raw_storage_providers_evp_outputs.explode("provider_id")[
        ["storage_provider_name", "provider_id", "green_score"]
    ].drop_duplicates(subset=["provider_id"])

    asset_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.shape[0]})


@dg.asset(compute_kind="python")
def raw_storage_providers_filrep_reputation(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    """
    Storage Provider reputation data from Filrep (https://filrep.io).
    """

    url = "https://api.filrep.io/api/v1/miners"

    r = requests.get(url)

    try:
        storage_providers = pd.DataFrame(r.json()["miners"])
    except Exception:
        context.log.error(f"Error fetching data from {url}. Reason: {r.reason}")
        return dg.MaterializeResult()

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

    table_name = context.asset_key.to_user_string()

    query = f"""
    create or replace table raw.{table_name} as (
        select
            *
        from storage_providers
    );
    """

    context.log.info(f"Creating table {table_name}")

    with duckdb.get_connection() as conn:
        conn.execute(query)

    return dg.MaterializeResult(
        metadata={"dagster/row_count": storage_providers.shape[0]}
    )


@dg.asset(compute_kind="python")
def raw_spark_retrieval_success_rate(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
    httpx_filspark: HttpClientResource,
) -> dg.MaterializeResult:
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

        date_df = pd.DataFrame(httpx_filspark.get(url).json())
        date_df["date"] = day
        df = pd.concat([df, date_df], ignore_index=True)

    df.rename(columns={"miner_id": "provider_id"}, inplace=True)

    asset_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.shape[0]})
