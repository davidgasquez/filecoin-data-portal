from pathlib import Path

import dagster as dg
import pandas as pd
import requests
from dagster_duckdb import DuckDBResource


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
def raw_storage_provider_labels(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    """
    Storage Provider labels from the repository curated CSV.
    """
    csv_path = (
        Path(__file__).resolve().parents[2] / "data" / "storage_provider_labels.csv"
    )
    df = pd.read_csv(csv_path).convert_dtypes()

    asset_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.shape[0]})


@dg.asset(compute_kind="python")
def raw_onramp_mappings(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    """
    Onramp mappings. Mappings of onramp names to client ids from Google Sheets.

    The Google Sheet is manually curated and can be found here:

    https://docs.google.com/spreadsheets/d/1HSimhURXMpWypbtXOiRd6MoWaHiLVOkjbQqGB3YQN50
    """

    url = "https://docs.google.com/spreadsheets/d/1HSimhURXMpWypbtXOiRd6MoWaHiLVOkjbQqGB3YQN50/export?format=csv"
    df = pd.read_csv(url)

    df = df.rename(columns={"Onramp Name": "onramp_name", "Client ID": "client_id"})
    df = df[["onramp_name", "client_id"]]

    asset_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.shape[0]})


@dg.asset(compute_kind="python")
def raw_fil_price(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    base_url = (
        "https://coincodex.com/api/coincodexcoins/get_historical_data_by_slug/filecoin/"
    )

    start_date = "2020-01-01"
    end_date = pd.Timestamp.utcnow().strftime("%Y-%m-%d")

    url = f"{base_url}/{start_date}/{end_date}"

    r = requests.get(url)
    r.raise_for_status()
    data = r.json()

    df = pd.DataFrame(data["data"])
    df["time_start"] = pd.to_datetime(df["time_start"])
    df["time_end"] = pd.to_datetime(df["time_end"])
    df = df.sort_values("time_start").reset_index(drop=True)

    asset_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.shape[0]})
