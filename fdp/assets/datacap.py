import os

import httpx
import pandas as pd
from dagster import Output, MetadataValue, AssetExecutionContext, asset


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
def raw_datacap_allocators_registry(
    context: AssetExecutionContext,
) -> Output[pd.DataFrame]:
    """
    Allocators information from Datacap Registry API.
    """
    github_data_url = "https://api.github.com/repos/filecoin-project/Allocator-Registry/contents/Allocators"

    transport = httpx.HTTPTransport(retries=2)
    client = httpx.Client(transport=transport, timeout=30)

    response = client.get(github_data_url)

    files_data = []

    if response.status_code == 200:
        for file in response.json():
            if file["name"].endswith(".json"):
                file_response = client.get(file["download_url"])
                if file_response.status_code == 200:
                    try:
                        files_data.append(file_response.json())
                    except Exception as e:
                        context.log.error(f"Failed to parse JSON: {e}")
                        context.log.error(f"Response: {file_response.text}")

    df = pd.DataFrame(files_data[:-1])

    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})


@asset(compute_kind="python")
def raw_datacap_github_applications(
    context: AssetExecutionContext,
    raw_datacap_allocators_registry: pd.DataFrame,
) -> pd.DataFrame:
    """
    Applications information from the allocator repositories.
    """

    allocator_applications = pd.json_normalize(
        raw_datacap_allocators_registry["application"]  # type: ignore
    )

    allocator_repositories = allocator_applications["allocation_bookkeeping"]
    allocator_repositories = allocator_repositories.dropna()

    context.log.info(f"Found {len(allocator_repositories)} allocator repositories.")

    token = str(os.getenv("GITHUB_TOKEN"))

    transport = httpx.HTTPTransport(retries=2)
    client = httpx.Client(transport=transport, timeout=30)

    applications = []

    for repository in allocator_repositories:
        n = repository.split(".com/")[1]

        context.log.info(f"Fetching applications from {n}.")
        response = client.get(
            "https://api.github.com/repos/" + n + "/contents/applications",
            timeout=30,
            headers={"Authorization": "Bearer " + token},
        )

        if response.status_code == 200:
            for file in response.json():
                if file["name"].endswith(".json"):
                    file_response = client.get(
                        file["download_url"],
                        headers={"Authorization": "Bearer " + token},
                    )
                    if file_response.status_code == 200:
                        a = file_response.json()
                        a["github_organization"] = n.split("/")[0]
                        a["github_repository"] = n.split("/")[1]
                        applications.append(a)
                    else:
                        context.log.warning(
                            f"Failed to fetch file: {file['download_url']}."
                        )
                        context.log.warning(f"Status code: {file_response.status_code}")
                        context.log.warning(f"Response: {file_response.json()}")
        else:
            context.log.warning(f"Failed to fetch applications from {n}.")
            context.log.warning(f"Status code: {response.status_code}")
            context.log.warning(f"Response: {response.json()}")

    df = pd.DataFrame(applications)
    df = df.rename(columns=lambda x: x.lower().replace(" ", "_"))

    return df
