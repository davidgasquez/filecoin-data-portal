# asset.description = Raw eth logs from RIB daily chain data.

# asset.materialization = custom

# asset.column = address | Contract address that emitted the log.
# asset.column = blockHash | Hash of the block containing the log.
# asset.column = blockNumber | Block number as returned by the source in hex.
# asset.column = data | Hex-encoded non-indexed event payload.
# asset.column = logIndex | Log position within the block, as returned in hex.
# asset.column = removed | Whether the log was removed by a chain reorg.
# asset.column = topics | Indexed log topics as an array of hex strings.
# asset.column = transactionHash | Hash of the transaction that emitted the log.
# asset.column = transactionIndex | Transaction index within the block in hex.
# asset.column = file_date | Source partition date used to load this row.
# asset.column = source_etag | Source partition ETag; a changed ETag reloads it.

import datetime as dt
import shutil
import tempfile
import time
from pathlib import Path

import httpx
import pyarrow as pa

import fdp
from fdp.api import table_exists

BASE_URL = "https://chain.data.riba.plus/fil/mainnet/daily"
START_DATE = dt.date(2025, 8, 1)
TABLE = "raw.riba_eth_logs"
RETRY_STATUSES = {408, 429, 500, 502, 503, 504}


def build_url(day: dt.date) -> str:
    return f"{BASE_URL}/{day:%Y/%m/%d}/eth_getBlockReceipts.v1.r1.ndjson.brotli"


def daily_logs_select(path: Path, day: dt.date) -> str:
    return f"""
        with receipts as (
            select unnest(result) as receipt
            from read_ndjson_auto('{path}')
            where result is not null
        ), logs as (
            select unnest(receipt.logs) as log
            from receipts
        )
        select
            log.address,
            log.blockHash,
            log.blockNumber,
            log.data,
            log.logIndex,
            log.removed,
            log.topics,
            log.transactionHash,
            log.transactionIndex,
            date '{day}' as file_date
        from logs
    """


def head(client: httpx.Client, url: str) -> httpx.Response:
    for attempt in range(4):
        try:
            resp = client.head(url)
            if resp.status_code not in RETRY_STATUSES:
                return resp
        except httpx.TransportError:
            pass
        time.sleep(2**attempt)
    return client.head(url)


def download(client: httpx.Client, url: str, path: Path) -> tuple[str, str]:
    # Fetch the smaller stored Brotli object instead of a decompressed HTTP stream.
    for attempt in range(5):
        if attempt:
            time.sleep(2**attempt)
        last = attempt == 4
        try:
            with client.stream("GET", url, headers={"Accept-Encoding": "br"}) as resp:
                if resp.status_code in RETRY_STATUSES and not last:
                    continue
                resp.raise_for_status()
                encoding = resp.headers.get("content-encoding", "identity")
                if encoding not in {"br", "identity"}:
                    raise ValueError(f"Unexpected RIBA encoding {encoding} for {url}")
                with path.open("wb") as f:
                    for chunk in resp.iter_raw():
                        f.write(chunk)
                etag = resp.headers["etag"].removeprefix("W/").strip('"')
                return encoding, etag
        except httpx.TransportError:
            if last:
                raise
    raise AssertionError


def loaded_etags() -> dict[dt.date, str]:
    with fdp.db_connection() as conn:
        if not table_exists(conn, "raw", "riba_eth_logs"):
            return {}
        conn.execute(f"alter table {TABLE} add column if not exists source_etag text")
        rows = conn.execute(
            f"select file_date, any_value(source_etag) from {TABLE} group by 1"
        ).fetchall()
    return dict(rows)


def replace_partition(conn, client: httpx.Client, url: str, day: dt.date) -> None:
    print(f"Loading RIBA eth logs for {day}", flush=True)
    with tempfile.TemporaryDirectory() as tmp:
        body, ndjson = Path(tmp, "logs.body"), Path(tmp, "logs.ndjson")
        encoding, etag = download(client, url, body)
        if encoding == "br":
            with (
                pa.input_stream(str(body), compression="brotli") as src,
                ndjson.open("wb") as dst,
            ):
                shutil.copyfileobj(src, dst)
        else:
            body.rename(ndjson)
        select_sql = daily_logs_select(ndjson, day)
        conn.execute(f"create or replace temp table riba_partition as {select_sql}")
    # Daily mainnet partitions always have logs; empty means a broken source file.
    if conn.execute("select count(*) from riba_partition").fetchone()[0] == 0:
        raise ValueError(f"Empty RIBA partition for {day}")
    conn.execute(
        f"create table if not exists {TABLE} as "
        "select *, ''::text as source_etag from riba_partition limit 0"
    )
    conn.execute("begin")
    conn.execute(f"delete from {TABLE} where file_date = ?", [day])
    conn.execute(
        f"insert into {TABLE} by name "
        "select *, ?::text as source_etag from riba_partition",
        [etag],
    )
    conn.execute("commit")
    conn.execute("drop table riba_partition")


def eth_logs() -> None:
    latest_day = dt.datetime.now(dt.UTC).date() - dt.timedelta(days=1)
    loaded = loaded_etags()

    with fdp.db_connection() as conn:
        conn.execute("create schema if not exists raw")

        with httpx.Client(follow_redirects=True, timeout=30) as client:
            day = START_DATE
            while day <= latest_day:
                url = build_url(day)
                resp = head(client, url)
                if resp.status_code != 404:
                    resp.raise_for_status()
                    # Weak and strong forms differ only by encoding negotiation.
                    etag = resp.headers["etag"].removeprefix("W/").strip('"')
                    if loaded.get(day) != etag:
                        replace_partition(conn, client, url, day)
                day += dt.timedelta(days=1)
