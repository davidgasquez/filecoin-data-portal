import dagster as dg
import httpx
import polars as pl
from dagster_duckdb import DuckDBResource

from fdp.resources import HttpClientResource


@dg.asset(compute_kind="python")
def raw_datacapstats_verified_clients(
    context: dg.AssetExecutionContext, duckdb_datacapstats: DuckDBResource
) -> dg.MaterializeResult:
    """
    Verified Clients information from Datacapstats API.
    """

    url = "https://api.datacapstats.io/api/getVerifiedClients"

    data = httpx.get(url).json()
    df = pl.DataFrame(data["data"], infer_schema_length=None)

    asset_name = context.asset_key.to_user_string()

    with duckdb_datacapstats.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    context.log.info(f"Persisted {df.height} rows to raw.{asset_name}")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.height})


@dg.asset(compute_kind="python")
def raw_datacapstats_verifiers(
    context: dg.AssetExecutionContext, duckdb_datacapstats: DuckDBResource
) -> dg.MaterializeResult:
    """
    Allocator (verifiers) information from Datacapstats API.
    """
    url = "https://api.datacapstats.io/api/getVerifiers"

    data = httpx.get(url).json()
    df = pl.DataFrame(data["data"], infer_schema_length=None)

    asset_name = context.asset_key.to_user_string()

    with duckdb_datacapstats.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    context.log.info(f"Persisted {df.height} rows to raw.{asset_name}")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.height})


@dg.asset(compute_kind="python")
def raw_datacap_allocators_registry(
    context: dg.AssetExecutionContext, duckdb_datacapstats: DuckDBResource
) -> dg.MaterializeResult:
    """
    Allocators information from the Allocator Registry GitHub repository.
    """

    github_data_url = "https://api.github.com/repos/filecoin-project/Allocator-Registry/contents/Allocators"

    transport = httpx.HTTPTransport(retries=2, verify=False)
    client = httpx.Client(transport=transport, timeout=30, follow_redirects=True)

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
                        context.log.warning(f"Failed to parse JSON for {file['name']}: {e}")
                else:
                    context.log.warning(f"Failed to fetch file: {file['download_url']}")
                    context.log.warning(f"Status code: {file_response.status_code}")
    else:
        context.log.error("Failed to fetch allocator registry from GitHub")
        context.log.error(f"Status code: {response.status_code}")
        context.log.error(f"Response: {response.text}")
        raise Exception(f"GitHub API request failed with status {response.status_code}")

    df = pl.DataFrame(files_data[:-1], strict=False)

    asset_name = context.asset_key.to_user_string()

    with duckdb_datacapstats.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    context.log.info(f"Persisted {df.height} rows to raw.{asset_name}")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.height})


@dg.asset(compute_kind="python")
def raw_datacap_github_applications(
    context: dg.AssetExecutionContext,
    httpx_datacapstats: HttpClientResource,
    duckdb_datacapstats: DuckDBResource,
) -> dg.MaterializeResult:
    """
    Applications information from the allocator repositories.
    """

    with duckdb_datacapstats.get_connection() as con:
        allocator_repositories = (
            con.sql("""
                select
                    application ->> '$.allocation_bookkeeping' as allocation_bookkeeping
                from raw.raw_datacap_allocators_registry
                where allocation_bookkeeping is not null
            """)
            .pl()["allocation_bookkeeping"]
            .to_list()
        )

    applications = []

    for repository in allocator_repositories:
        context.log.info(f"Fetching applications from {repository}.")

        try:
            n = repository.split(".com/")[1]
        except IndexError:
            context.log.warning(f"Failed to parse repository name from {repository}.")
            continue

        context.log.info(f"Fetching applications from {n}.")
        response = httpx_datacapstats.get(
            "https://api.github.com/repos/" + n + "/contents/applications"
        )

        if response.status_code == 200:
            for file in response.json():
                if file["name"].endswith(".json"):
                    file_response = httpx_datacapstats.get(file["download_url"])
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

    context.log.info(f"Fetched {len(applications)} applications.")

    df = pl.DataFrame(applications)
    df = df.rename(mapping=lambda x: x.lower().replace(" ", "_"))

    asset_name = context.asset_key.to_user_string()

    with duckdb_datacapstats.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    context.log.info(f"Persisted {df.height} rows to raw.{asset_name}")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.height})
