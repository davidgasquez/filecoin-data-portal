import pandas as pd
from dagster import Output, MetadataValue, asset


@asset(compute_kind="python")
def raw_datacapstats_verified_clients() -> Output[pd.DataFrame]:
    """
    Verified Clients information from Datacapstats API.
    """
    url = "https://api.datacapstats.io/api/getVerifiedClients"

    data = pd.read_json(url, typ="series")["data"]
    df = pd.json_normalize(data)
    df["allowanceArray"] = df["allowanceArray"]

    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})


@asset(compute_kind="python")
def raw_datacapstats_verifiers() -> Output[pd.DataFrame]:
    """
    Allocator (verifiers) information from Datacapstats API.
    """
    url = "https://api.datacapstats.io/api/getVerifiers"

    data = pd.read_json(url, typ="series")["data"]
    df = pd.json_normalize(data).convert_dtypes()

    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})
