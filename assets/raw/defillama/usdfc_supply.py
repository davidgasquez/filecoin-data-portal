# asset.description = Daily USDFC circulating supply on Filecoin from DefiLlama.
# https://stablecoins.llama.fi/stablecoin/248

# asset.materialization = dataframe
# asset.keep_existing_on_failure = true

# asset.column = date | UTC date of the DefiLlama snapshot.
# asset.column = snapshot_at | DefiLlama snapshot timestamp, latest one on the date.
# asset.column = circulating_usdfc | Circulating USDFC, in tokens.

# asset.not_null = date
# asset.not_null = snapshot_at
# asset.unique = date
# asset.assert = circulating_usdfc >= 0
# asset.assert = cast(snapshot_at as date) = date

import datetime as dt

import httpx
import polars as pl

URL = "https://stablecoins.llama.fi/stablecoin/248"


def usdfc_supply() -> pl.DataFrame:
    today = dt.datetime.now(dt.UTC).date()
    payload = httpx.get(URL, timeout=60).raise_for_status().json()
    if payload["symbol"] != "USDFC":
        raise ValueError(f"Unexpected stablecoin {payload['symbol']}")
    rows = payload["chainBalances"]["Filecoin"]["tokens"]
    return (
        pl
        .DataFrame(
            [
                (row["date"], (row.get("circulating") or {}).get("peggedUSD"))
                for row in rows
            ],
            schema={"snapshot": pl.Int64, "circulating_usdfc": pl.Float64},
            orient="row",
        )
        .with_columns(snapshot_at=pl.from_epoch("snapshot", time_unit="s"))
        .with_columns(date=pl.col("snapshot_at").dt.date())
        .filter(pl.col("date") < today)
        .sort("snapshot_at")
        .group_by("date")
        .last()
        .select("date", "snapshot_at", "circulating_usdfc")
        .sort("date", descending=True)
    )
