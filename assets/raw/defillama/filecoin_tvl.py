# asset.description = Daily Filecoin DeFi TVL from DefiLlama.
# Excludes liquid staking and double counted TVL.
# https://api.llama.fi/v2/historicalChainTvl/Filecoin

# asset.materialization = dataframe
# asset.keep_existing_on_failure = true

# asset.column = date | UTC date of the DefiLlama snapshot.
# asset.column = snapshot_at | DefiLlama snapshot timestamp, latest one on the date.
# asset.column = tvl_usd | Filecoin DeFi TVL, in USD.

# asset.not_null = date
# asset.not_null = snapshot_at
# asset.unique = date
# asset.assert = tvl_usd >= 0
# asset.assert = cast(snapshot_at as date) = date

import datetime as dt

import httpx
import polars as pl

URL = "https://api.llama.fi/v2/historicalChainTvl/Filecoin"


def filecoin_tvl() -> pl.DataFrame:
    today = dt.datetime.now(dt.UTC).date()
    rows = httpx.get(URL, timeout=60).raise_for_status().json()
    return (
        pl
        .DataFrame(
            [(row["date"], row["tvl"]) for row in rows],
            schema={"snapshot": pl.Int64, "tvl_usd": pl.Float64},
            orient="row",
        )
        .with_columns(snapshot_at=pl.from_epoch("snapshot", time_unit="s"))
        .with_columns(date=pl.col("snapshot_at").dt.date())
        .filter(pl.col("date") < today)
        .sort("snapshot_at")
        .group_by("date")
        .last()
        .select("date", "snapshot_at", "tvl_usd")
        .sort("date", descending=True)
    )
