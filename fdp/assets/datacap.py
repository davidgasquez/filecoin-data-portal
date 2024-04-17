import pandas as pd
import requests
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


@asset(compute_kind="python")
def raw_datacap_allocators_registry() -> Output[pd.DataFrame]:
    """
    Allocators information from Datacap Registry API.
    """
    github_data_url = "https://api.github.com/repos/filecoin-project/Allocator-Registry/contents/Allocators"
    response = requests.get(github_data_url)

    files_data = []

    if response.status_code == 200:
        for file in response.json():
            if file["name"].endswith(".json"):
                file_response = requests.get(file["download_url"])
                if file_response.status_code == 200:
                    files_data.append(file_response.json())

    df = pd.DataFrame(files_data[:-1])

    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})
