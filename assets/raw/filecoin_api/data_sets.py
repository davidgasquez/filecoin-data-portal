# asset.description = Current Warm Storage data set snapshot from the Filecoin API.
# https://api.filecoin.io/openapi.json

# asset.materialization = dataframe
# asset.keep_existing_on_failure = true

# asset.column = data_set_id | Data set identifier.
# asset.column = provider_id | Service provider registry identifier.
# asset.column = owner | Client address that pays for the data set.
# asset.column = source | Source metadata value, if any.
# asset.column = metadata | Current data set metadata as JSON, if any.
# asset.column = with_cdn | Whether CDN is currently enabled.
# asset.column = with_ipfs_indexing | Whether IPFS indexing is requested.
# asset.column = pdp_end_epoch | PDP payment end epoch, if terminated.
# asset.column = pdp_rail_id | Filecoin Pay PDP rail identifier.
# asset.column = cache_miss_rail_id | Cache-miss rail identifier, if any.
# asset.column = cdn_rail_id | Filecoin Pay CDN rail identifier, if any.
# asset.column = deleted | Whether the data set is deleted.
# asset.column = created_at_block | Creation block number.
# asset.column = updated_at_block | Last indexer update block number.
# asset.column = indexed_block | API indexer head before paging, not the state block.
# asset.column = observed_at | UTC fetch timestamp.

# asset.not_null = data_set_id
# asset.not_null = pdp_rail_id
# asset.not_null = deleted
# asset.not_null = indexed_block
# asset.not_null = observed_at
# asset.unique = data_set_id

import datetime as dt
import json

import httpx
import polars as pl

URL = "https://api.filecoin.io/mainnet"
COLUMNS = {
    "dataSetId": ("data_set_id", pl.Int64),
    "providerId": ("provider_id", pl.Int64),
    "owner": ("owner", pl.String),
    "source": ("source", pl.String),
    "metadata": ("metadata", pl.String),
    "withCdn": ("with_cdn", pl.Boolean),
    "withIpfsIndexing": ("with_ipfs_indexing", pl.Boolean),
    "pdpEndEpoch": ("pdp_end_epoch", pl.Int64),
    "pdpRailId": ("pdp_rail_id", pl.Int64),
    "cacheMissRailId": ("cache_miss_rail_id", pl.Int64),
    "cdnRailId": ("cdn_rail_id", pl.Int64),
    "deleted": ("deleted", pl.Boolean),
    "createdAtBlock": ("created_at_block", pl.Int64),
    "updatedAtBlock": ("updated_at_block", pl.Int64),
}


def data_sets() -> pl.DataFrame:
    observed_at = dt.datetime.now(dt.UTC).replace(tzinfo=None)
    with httpx.Client(base_url=URL, timeout=60) as client:
        status = client.get("/status").raise_for_status().json()
        rows, cursor = [], None
        while True:
            params = {"limit": 200} | ({"cursor": cursor} if cursor else {})
            page = client.get("/data-sets", params=params).raise_for_status().json()
            rows += page["data"]
            cursor = page["nextCursor"]
            if cursor is None:
                break

    for row in rows:
        if row["metadata"] is not None:
            row["metadata"] = json.dumps(row["metadata"], sort_keys=True)
    return (
        pl
        .DataFrame(rows, infer_schema_length=None)
        .select(pl.col(k).cast(t).alias(name) for k, (name, t) in COLUMNS.items())
        .with_columns(
            pl.col("owner").str.to_lowercase(),
            indexed_block=pl.lit(
                status["data"]["indexers"][0]["latest"]["blockNumber"], pl.Int64
            ),
            observed_at=pl.lit(observed_at),
        )
        .sort("data_set_id", descending=True)
    )
