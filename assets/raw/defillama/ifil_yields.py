# asset.description = Daily GLIF iFIL base yield from DefiLlama.
# https://yields.llama.fi/chart/53048f5b-7b0a-4917-b283-c49bef77e580

# asset.materialization = dataframe
# asset.keep_existing_on_failure = true

# asset.column = date | UTC observation date.
# asset.column = observed_at | DefiLlama observation timestamp, latest one on the date.
# asset.column = base_apy | Annualized base yield as a fraction, excluding rewards.

# asset.not_null = date
# asset.not_null = observed_at
# asset.unique = date
# asset.assert = cast(observed_at as date) = date
# asset.assert = base_apy >= 0

import datetime as dt

import httpx
import polars as pl

URL = "https://yields.llama.fi/chart/53048f5b-7b0a-4917-b283-c49bef77e580"


def ifil_yields() -> pl.DataFrame:
    today = dt.datetime.now(dt.UTC).date()
    rows = httpx.get(URL, timeout=60).raise_for_status().json()["data"]
    return (
        pl
        .DataFrame(
            [(row["timestamp"], row["apyBase"]) for row in rows],
            schema={"observed_at": pl.String, "apy_base": pl.Float64},
            orient="row",
        )
        .with_columns(
            observed_at=pl
            .col("observed_at")
            .str.to_datetime(time_zone="UTC")
            .dt.replace_time_zone(None)
        )
        .with_columns(date=pl.col("observed_at").dt.date())
        .filter(pl.col("date") < today)
        .sort("observed_at")
        .group_by("date")
        .last()
        .select("date", "observed_at", base_apy=pl.col("apy_base") / 100)
        .sort("date", descending=True)
    )
