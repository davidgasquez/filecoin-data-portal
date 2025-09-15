import dagster as dg
import httpx
import polars as pl
from urllib.parse import urlparse
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

    def _parse_repo_slug(value: str) -> str | None:
        """Return an "owner/repo" slug from various possible inputs.

        Handles full GitHub URLs (with extra path segments like `/issues`,
        `/tree/branch/...`, etc.) as well as plain `owner/repo` strings.
        """

        if not value:
            return None

        # If it looks like a URL, extract path parts after the host
        if value.startswith("http://") or value.startswith("https://"):
            try:
                parsed = urlparse(value)
                if parsed.netloc.endswith("github.com"):
                    parts = [p for p in parsed.path.split("/") if p]
                    if len(parts) >= 2:
                        return f"{parts[0]}/{parts[1]}"
            except Exception:
                return None

        # Otherwise assume it could be already a slug; take first two path parts
        parts = [p for p in value.split("/") if p]
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
        return None

    applications: list[dict] = []

    for repository in allocator_repositories:
        context.log.info(f"Fetching applications from {repository}.")

        slug = _parse_repo_slug(repository)
        if not slug:
            context.log.warning(
                f"Could not extract repo slug from '{repository}'. Skipping."
            )
            continue

        owner, repo = slug.split("/", 1)
        context.log.info(f"Resolved repo: {owner}/{repo}.")

        try:
            response = httpx_datacapstats.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents/applications"
            )
        except httpx.HTTPError as e:
            context.log.warning(
                f"HTTP error while listing applications for {owner}/{repo}: {e}"
            )
            continue

        if response.status_code == 200:
            try:
                listing = response.json()
            except Exception as e:
                context.log.warning(
                    f"Failed to parse directory listing JSON for {owner}/{repo}: {e}"
                )
                context.log.debug(f"Response text: {response.text}")
                continue

            for file in listing:
                if file.get("name", "").endswith(".json") and file.get("download_url"):
                    try:
                        file_response = httpx_datacapstats.get(file["download_url"])
                    except httpx.HTTPError as e:
                        context.log.warning(
                            f"HTTP error fetching {file.get('download_url')}: {e}"
                        )
                        continue

                    if file_response.status_code == 200:
                        try:
                            a = file_response.json()
                        except Exception as e:
                            context.log.warning(
                                f"Failed to parse JSON from {file.get('download_url')}: {e}"
                            )
                            context.log.debug(
                                f"File response text: {file_response.text[:1000]}"
                            )
                            continue

                        a["github_organization"] = owner
                        a["github_repository"] = repo
                        applications.append(a)
                    else:
                        context.log.warning(
                            f"Failed to fetch file: {file.get('download_url')}"
                        )
                        context.log.warning(
                            f"Status code: {file_response.status_code}"
                        )
                        context.log.debug(f"Response text: {file_response.text}")
        else:
            context.log.warning(
                f"Failed to fetch applications directory for {owner}/{repo}."
            )
            context.log.warning(f"Status code: {response.status_code}")
            context.log.debug(f"Response text: {response.text}")

    context.log.info(f"Fetched {len(applications)} applications.")

    if not applications:
        context.log.warning(
            "No applications fetched from any allocator repo. Skipping write."
        )
        return dg.MaterializeResult(metadata={"dagster/row_count": 0})

    df = pl.DataFrame(applications)
    df = df.rename(mapping=lambda x: x.lower().replace(" ", "_"))

    asset_name = context.asset_key.to_user_string()

    with duckdb_datacapstats.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    context.log.info(f"Persisted {df.height} rows to raw.{asset_name}")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.height})
