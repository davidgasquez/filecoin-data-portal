import polars as pl

from fdp import dataset, fetch_json


@dataset
def datacapstats_verified_clients() -> pl.DataFrame:
    """
    Verified Clients information from Datacapstats API.
    """

    url = "https://api.datacapstats.io/api/getVerifiedClients"
    return pl.DataFrame(
        data=fetch_json(url)["data"],
        infer_schema_length=None,
    )
