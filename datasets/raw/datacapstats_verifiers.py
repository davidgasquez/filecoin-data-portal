import polars as pl

from fdp import dataset, fetch_json


@dataset
def datacapstats_verifiers() -> pl.DataFrame:
    """
    Allocator (verifiers) information from Datacapstats API.
    """

    url = "https://api.datacapstats.io/api/getVerifiers"
    return pl.DataFrame(
        data=fetch_json(url)["data"],
        infer_schema_length=None,
    )
