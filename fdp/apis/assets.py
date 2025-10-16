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
def raw_storage_providers_evp_outputs(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    """
    Storage Providers Retrieves all existing Energy Validation Process outputs.
    """
    try:
        r = requests.get(
            "https://sp-outputs-api.vercel.app/api/evp-outputs", verify=False
        )
        r.raise_for_status()
    except requests.RequestException as exc:
        context.log.error(
            "Failed to refresh Energy Validation Process outputs. "
            f"Continuing with previous table contents. Reason: {exc}"
        )
        return dg.MaterializeResult(metadata={"dagster/row_count": 0})

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
