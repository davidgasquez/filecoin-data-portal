import pandas as pd
from dagster import Output, MetadataValue, asset

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


@asset(compute_kind="API")
def dune_metrics(dune: DuneResource, filecoin_daily_metrics: pd.DataFrame) -> None:
    """
    Uploads allo deployments to Dune.
    """
    dune.upload_df(filecoin_daily_metrics, "filecoin_daily_metrics")
