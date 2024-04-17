import pandas as pd
from dagster import Output, MetadataValue, asset
from dagster_duckdb import DuckDBResource

from fdp.resources import DuneResource


@asset(compute_kind="python")
def raw_storage_providers_location_provider_quest() -> Output[pd.DataFrame]:
    """
    Storage Providers location information from Provider Quest (https://provider.quest).
    """
    url = "https://geoip.feeds.provider.quest/synthetic-locations-latest.json"
    all_df = pd.read_json(url, typ="series")
    df = pd.json_normalize(all_df["providerLocations"])
    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})


@asset(compute_kind="API", deps=["filecoin_daily_metrics"])
def dune_metrics(dune: DuneResource, duckdb: DuckDBResource) -> None:
    """
    Uploads allo deployments to Dune.
    """
    with duckdb.get_connection() as conn:
        filecoin_daily_metrics = conn.execute(
            "select * from filecoin_daily_metrics"
        ).df()

    dune.upload_df(filecoin_daily_metrics, "filecoin_daily_metrics")
