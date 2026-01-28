import polars as pl

from fdp.http import fetch_json


def datacapstats_verifiers() -> pl.DataFrame:
    """
    Allocator (verifiers) information from Datacapstats API.
    """

    url = "https://api.datacapstats.io/api/getVerifiers"
    return pl.DataFrame(
        data=fetch_json(url)["data"],
        infer_schema_length=None,
    )
