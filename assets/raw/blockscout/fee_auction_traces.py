# asset.description = Blockscout call traces of Filecoin Pay fee-auction candidates.

# asset.depends = raw.contracts_registry
# asset.depends = raw.riba_eth_logs
# asset.depends = raw.solstice_deployments

# asset.materialization = custom
# asset.keep_existing_on_failure = true

# asset.column = transaction_hash | Candidate tx; NULL on the empty-scan marker row.
# asset.column = block_number | Executing epoch reported by discovery.
# asset.column = discovered_by | Candidate sources (riba_transfer, blockscout_call).
# asset.column = block_hash | Trace block hash; NULL while the trace is unavailable.
# asset.column = transaction_index | Trace message position in the tipset.
# asset.column = trace | Parity-style trace JSON; NULL while unavailable (retried).
# asset.column = scanned_to_block | Last epoch covered by this discovery run.
# asset.column = source_url | Blockscout raw-trace URL.
# asset.column = fetched_at | Timestamp of the trace fetch.

# asset.unique = transaction_hash

"""Candidates: Transfer(from = Pay) logs in RIBA, plus Blockscout's index of nested
burnForFees calls (catches claims that move no tokens). Discovery stops at the last
RIBA day so traces and logs describe the same epochs."""

import datetime as dt
import time

import httpx
import polars as pl

import fdp
from fdp.api import table_exists

TABLE = "raw.blockscout_fee_auction_traces"
BASE_URL = "https://filecoin.blockscout.com/api/v2"
GENESIS = 1598306400
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
BURN_FOR_FEES = "0x1a257300"
SCHEMA = {
    "transaction_hash": pl.String,
    "block_number": pl.Int64,
    "discovered_by": pl.String,
    "block_hash": pl.String,
    "transaction_index": pl.Int64,
    "trace": pl.String,
    "scanned_to_block": pl.Int64,
    "source_url": pl.String,
    "fetched_at": pl.Datetime,
}


def get(client: httpx.Client, url: str, params: dict | None = None) -> httpx.Response:
    for attempt in range(5):
        response = client.get(url, params=params)
        if response.status_code != 429:
            return response
        time.sleep(2**attempt)
    return response.raise_for_status()


def at(epoch: int) -> dt.datetime:
    return dt.datetime.fromtimestamp(GENESIS + epoch * 30, dt.UTC)


def fee_auction_traces() -> None:
    yesterday = dt.datetime.now(dt.UTC).date() - dt.timedelta(days=1)
    with fdp.db_connection() as conn:
        pays = sorted(
            r[0]
            for r in conn.execute(
                "select distinct lower(address) from raw.contracts_registry "
                "where contract_name = 'filecoin_pay_v1'"
            ).fetchall()
        )
        ((activation, last_day),) = conn.execute(
            "select (select activation_epoch from raw.solstice_deployments "
            "where chain_id = 314), (select max(file_date) from raw.riba_eth_logs)"
        ).fetchall()
        last_day = min(last_day, yesterday)
        midnight = dt.datetime.combine(last_day + dt.timedelta(days=1), dt.time())
        scanned_to = (
            int(midnight.replace(tzinfo=dt.UTC).timestamp()) - GENESIS
        ) // 30 - 1
        candidates = {
            tx: (block, {"riba_transfer"})
            for tx, block in conn.execute(
                """
                select lower(transactionHash), min(blockNumber::bigint)
                from raw.riba_eth_logs
                where file_date >= ?
                  and lower(topics[1]) = ?
                  and lower(topics[2]) in (
                      select '0x' || repeat('0', 24) || substr(unnest(?::varchar[]), 3)
                  )
                  and not removed
                  and blockNumber::bigint between ? and ?
                group by 1
                """,
                [at(activation).date(), TRANSFER_TOPIC, pays, activation, scanned_to],
            ).fetchall()
        }
        cached = {}
        if table_exists(conn, "raw", "blockscout_fee_auction_traces"):
            cached = {
                r[0]: r[1:]
                for r in conn.execute(
                    "select transaction_hash, block_hash, transaction_index, trace, "
                    f"fetched_at from {TABLE} where trace is not null"
                ).fetchall()
            }

    rows = []
    with httpx.Client(follow_redirects=True, timeout=60) as client:
        for pay in pays:
            params = {
                "methods": BURN_FOR_FEES,
                "to_address_hashes_to_include": pay,
                "age_from": at(activation).isoformat(),
                "age_to": at(scanned_to + 1).isoformat(),
            }
            while True:
                url = f"{BASE_URL}/advanced-filters"
                page = get(client, url, params).raise_for_status().json()
                for item in page["items"]:
                    if activation <= item["block_number"] <= scanned_to:
                        _, sources = candidates.setdefault(
                            item["hash"].lower(), (item["block_number"], set())
                        )
                        sources.add("blockscout_call")
                if not page.get("next_page_params"):
                    break
                params = {**params, **page["next_page_params"]}

        for tx, (block, sources) in sorted(candidates.items()):
            url = f"{BASE_URL}/transactions/{tx}/raw-trace"
            if tx in cached:
                block_hash, position, trace, fetched_at = cached[tx]
            else:
                response = get(client, url)
                if response.status_code != 404:
                    response.raise_for_status()
                parsed = response.json() if response.status_code == 200 else None
                block_hash = position = trace = None  # Unavailable: retried next run.
                if parsed and parsed[0].get("transactionHash", "").lower() == tx:
                    block_hash = parsed[0]["blockHash"].lower()
                    position = parsed[0]["transactionPosition"]
                    trace = response.text
                fetched_at = dt.datetime.now(dt.UTC).replace(tzinfo=None)
            rows.append({
                "transaction_hash": tx,
                "block_number": block,
                "discovered_by": ",".join(sorted(sources)),
                "block_hash": block_hash,
                "transaction_index": position,
                "trace": trace,
                "scanned_to_block": scanned_to,
                "source_url": url,
                "fetched_at": fetched_at,
            })
    # The marker row keeps an empty successful scan distinct from no scan.
    frame = pl.DataFrame(rows or [{"scanned_to_block": scanned_to}], schema=SCHEMA)
    with fdp.db_connection() as conn:
        conn.execute("create schema if not exists raw")
        conn.register("frame", frame.to_arrow())
        conn.execute(f"create or replace table {TABLE} as select * from frame")
