# asset.description = Daily Filecoin TVL per DefiLlama protocol.
# https://api.llama.fi/protocol/{slug}

# asset.materialization = dataframe
# asset.keep_existing_on_failure = true

# asset.column = date | UTC date of the DefiLlama snapshot.
# asset.column = protocol | DefiLlama protocol slug.
# asset.column = category | DefiLlama protocol category.
# asset.column = snapshot_at | DefiLlama snapshot timestamp, latest one on the date.
# asset.column = tvl_usd | Protocol TVL on Filecoin, in USD.
# asset.column = tvl_fil | FIL in the protocol TVL on Filecoin, if broken down.

# asset.not_null = date
# asset.not_null = protocol
# asset.not_null = snapshot_at
# asset.assert = tvl_usd >= 0
# asset.assert = tvl_fil >= 0
# asset.assert = cast(snapshot_at as date) = date

import datetime as dt

import httpx
import polars as pl

PROTOCOLS_URL = "https://api.llama.fi/protocols"
PROTOCOL_URL = "https://api.llama.fi/protocol/{slug}"
CHAIN = "Filecoin"
SCHEMA = {
    "date": pl.Date,
    "protocol": pl.String,
    "category": pl.String,
    "snapshot_at": pl.Datetime,
    "tvl_usd": pl.Float64,
    "tvl_fil": pl.Float64,
}


def daily_points(series: dict, today: dt.date) -> dict[dt.date, tuple]:
    tokens = {row["date"]: row["tokens"] for row in series.get("tokens") or []}
    points = {}
    for row in sorted(series.get("tvl") or [], key=lambda row: row["date"]):
        snapshot_at = dt.datetime.fromtimestamp(row["date"], dt.UTC)
        if snapshot_at.date() < today:
            fil = (tokens.get(row["date"]) or {}).get("FIL")
            points[snapshot_at.date()] = (snapshot_at, row["totalLiquidityUSD"], fil)
    return points


def filecoin_protocol_tvl() -> pl.DataFrame:
    today = dt.datetime.now(dt.UTC).date()
    rows = []
    with httpx.Client(timeout=120) as client:
        protocols = client.get(PROTOCOLS_URL).raise_for_status().json()
        for protocol in protocols:
            if (
                CHAIN not in (protocol.get("chains") or [])
                or protocol["category"] == "CEX"
            ):
                continue
            url = PROTOCOL_URL.format(slug=protocol["slug"])
            payload = client.get(url).raise_for_status().json()
            series = payload["chainTvls"].get(CHAIN) or {}
            for date, (snapshot_at, tvl_usd, tvl_fil) in daily_points(
                series, today
            ).items():
                rows.append({
                    "date": date,
                    "protocol": protocol["slug"],
                    "category": protocol["category"],
                    "snapshot_at": snapshot_at.replace(tzinfo=None),
                    "tvl_usd": tvl_usd,
                    "tvl_fil": tvl_fil,
                })

    return pl.DataFrame(rows, schema=SCHEMA).sort(
        ["date", "tvl_usd"], descending=True, nulls_last=True
    )
