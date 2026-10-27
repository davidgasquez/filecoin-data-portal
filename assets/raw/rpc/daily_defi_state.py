# asset.description = End-of-day GLIF Infinity Pool and axlUSDC state from JSON-RPC.
# Public RPCs keep only recent state, so dates accrue daily from the first run.

# asset.materialization = custom
# asset.keep_existing_on_failure = true

# asset.column = date | UTC date.
# asset.column = block_number | Last non-null epoch of the date, whose state is read.
# asset.column = block_hash | Hash of the block used for the reads.
# asset.column = block_at | Block timestamp.
# asset.column = glif_pool_total_assets_fil | GLIF pool totalAssets, in FIL.
# asset.column = glif_pool_total_borrowed_fil | GLIF pool totalBorrowed, in FIL.
# asset.column = glif_pool_borrowable_fil | GLIF pool totalBorrowableAssets, in FIL.
# asset.column = usdc_axl_total_supply | axlUSDC totalSupply on Filecoin, in tokens.
# asset.column = fetched_at | Fetch timestamp.

# asset.not_null = date
# asset.not_null = block_number
# asset.not_null = block_hash
# asset.not_null = block_at
# asset.not_null = glif_pool_total_assets_fil
# asset.not_null = glif_pool_total_borrowed_fil
# asset.not_null = glif_pool_borrowable_fil
# asset.not_null = usdc_axl_total_supply
# asset.unique = date
# asset.unique = block_number
# asset.assert = cast(block_at as date) = date

import datetime as dt
from typing import Any

import httpx

import fdp
from fdp.api import table_exists

TABLE = "raw.rpc_daily_defi_state"
RPC_URLS = ("https://api.node.glif.io/rpc/v1", "https://api.chain.love/rpc/v1")
GENESIS_TIMESTAMP = 1598306400
FINALITY_EPOCHS = 900
GLIF_POOL = "0xe764Acf02D8B7c21d2B6A8f0a96C78541e0DC3fd"
USDC_AXL = "0xeb466342c4d449bc9f53a865d5cb90586f405215"
CALLS = {
    "glif_pool_total_assets_fil": (GLIF_POOL, "0x01e1d114", 18),
    "glif_pool_total_borrowed_fil": (GLIF_POOL, "0x4c19386c", 18),
    "glif_pool_borrowable_fil": (GLIF_POOL, "0x86a2c988", 18),
    "usdc_axl_total_supply": (USDC_AXL, "0x18160ddd", 6),
}


def rpc(client: httpx.Client, url: str, method: str, params: list) -> Any:
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    body = client.post(url, json=payload).raise_for_status().json()
    if "error" in body:
        raise RuntimeError(f"{method}: {body['error']}")
    return body["result"]


def last_epoch(day: dt.date) -> int:
    next_day = dt.datetime.combine(day + dt.timedelta(days=1), dt.time(), dt.UTC)
    return (int(next_day.timestamp()) - GENESIS_TIMESTAMP) // 30 - 1


def day_state(client: httpx.Client, url: str, day: dt.date) -> dict:
    # Returns the last non-null tipset at or before the epoch (skips null rounds).
    tipset = rpc(
        client, url, "Filecoin.ChainGetTipSetByHeight", [last_epoch(day), None]
    )
    block = rpc(client, url, "eth_getBlockByNumber", [hex(tipset["Height"]), False])
    block_at = dt.datetime.fromtimestamp(int(block["timestamp"], 16), dt.UTC)
    if block_at.date() != day:
        raise RuntimeError(f"No closing block on {day}")
    row = {
        "date": day,
        "block_number": int(block["number"], 16),
        "block_hash": block["hash"],
        "block_at": block_at.replace(tzinfo=None),
    }
    for column, (address, selector, decimals) in CALLS.items():
        call = {"to": address, "data": selector}
        value = rpc(client, url, "eth_call", [call, {"blockHash": block["hash"]}])
        row[column] = int(str(value), 16) / 10**decimals
    return row


def daily_defi_state() -> None:
    with fdp.db_connection() as conn:
        loaded = set()
        if table_exists(conn, "raw", "rpc_daily_defi_state"):
            rows = conn.sql(f"select date from {TABLE}").fetchall()
            loaded = {row[0] for row in rows}
    # Public RPCs only serve recent state, so only yesterday is read.
    yesterday = dt.datetime.now(dt.UTC).date() - dt.timedelta(days=1)
    if yesterday in loaded:
        return

    last_error: Exception | None = None
    for url in RPC_URLS:
        try:
            with httpx.Client(timeout=60) as client:
                head = int(str(rpc(client, url, "eth_blockNumber", [])), 16)
                if last_epoch(yesterday) > head - FINALITY_EPOCHS:
                    raise RuntimeError(f"{yesterday} is not finalized at {head}")
                rows = [day_state(client, url, yesterday)]
            break
        except (httpx.HTTPError, RuntimeError) as error:
            last_error = error
    else:
        raise RuntimeError("DeFi state RPC reads failed") from last_error

    fetched_at = dt.datetime.now(dt.UTC).replace(tzinfo=None)
    with fdp.db_connection() as conn:
        conn.execute("create schema if not exists raw")
        conn.execute(f"""
            create table if not exists {TABLE} (
                date date,
                block_number bigint,
                block_hash text,
                block_at timestamp,
                glif_pool_total_assets_fil double,
                glif_pool_total_borrowed_fil double,
                glif_pool_borrowable_fil double,
                usdc_axl_total_supply double,
                fetched_at timestamp
            )
        """)
        for row in rows:
            conn.execute(
                f"insert into {TABLE} by name select $1::date as date, "
                "$2 as block_number, $3 as block_hash, $4 as block_at, "
                "$5 as glif_pool_total_assets_fil, $6 as glif_pool_total_borrowed_fil, "
                "$7 as glif_pool_borrowable_fil, $8 as usdc_axl_total_supply, "
                "$9 as fetched_at",
                [*row.values(), fetched_at],
            )
