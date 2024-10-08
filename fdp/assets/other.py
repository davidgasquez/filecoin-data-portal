import pandas as pd
import requests
from dagster import Output, MetadataValue, asset
from dagster_duckdb import DuckDBResource

from fdp.resources import DuneResource


@asset(compute_kind="python")
def raw_storage_providers_location_provider_quest() -> Output[pd.DataFrame]:
    """
    Storage Providers location information from Provider Quest (https://provider.quest).

    Synthetic locations documentation: https://observablehq.com/@jimpick/provider-quest-synthetic-locations
    """
    url = "https://provider-quest.s3.us-west-2.amazonaws.com/dist/geoip-lookups/synthetic-locations-latest.json"
    all_df = pd.read_json(url, typ="series")
    df = pd.json_normalize(all_df["providerLocations"])
    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})


@asset(compute_kind="python")
def raw_storage_providers_evp_outputs() -> Output[pd.DataFrame]:
    """
    Storage Providers Retrieves all existing Energy Validation Process outputs.
    """
    r = requests.get("https://sp-outputs-api.vercel.app/api/evp-outputs")
    r.raise_for_status()

    df = pd.DataFrame(r.json()["data"])

    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})


@asset(compute_kind="python")
def raw_storage_providers_energy_name_mapping(
    raw_storage_providers_evp_outputs: pd.DataFrame,
) -> Output[pd.DataFrame]:
    """
    Storage Providers Entities Mapping to Provider IDs.
    """
    raw_storage_providers_evp_outputs["provider_id"] = (
        raw_storage_providers_evp_outputs["miner_ids"].str.split(",")
    )

    df = raw_storage_providers_evp_outputs.explode("provider_id")[
        ["storage_provider_name", "provider_id", "green_score"]
    ].drop_duplicates(subset=["provider_id"])

    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})


@asset(compute_kind="API", deps=["filecoin_daily_metrics"])
def dune_metrics(dune: DuneResource, duckdb: DuckDBResource) -> None:
    """
    Uploads allo deployments to Dune.
    """
    with duckdb.get_connection() as conn:
        filecoin_daily_metrics = conn.execute("""
            select
                date,
                onboarded_data_pibs,
                unique_data_onboarded_data_pibs,
                unique_data_onboarded_ratio,
                data_on_active_deals_pibs,
                unique_data_on_active_deals_pibs,
                deals,
                unique_deal_making_clients,
                unique_deal_making_providers,
                active_deals,
                clients_with_active_deals,
                providers_with_active_deals,
                raw_power_pibs,
                quality_adjusted_power_pibs,
                verified_data_power_pibs,
                network_utilization_ratio,
                new_client_ids,
                new_provider_ids,
                ended_data_pibs,
                new_client_ids,
                new_provider_ids,
                new_piece_cids,
                mean_spark_retrieval_success_rate,
                providers_with_successful_retrieval,
                providers_with_retrieval_attempts
            from filecoin_daily_metrics
            where date > '2021-01-01'
        """).df()

    dune.upload_df(filecoin_daily_metrics, "filecoin_daily_metrics")
