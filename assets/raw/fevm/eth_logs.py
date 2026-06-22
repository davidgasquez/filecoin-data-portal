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

import datetime as dt

import httpx

import fdp
from fdp.api import table_exists

BASE_URL = "https://chain.data.riba.plus/fil/mainnet/daily"
START_DATE = dt.date(2025, 8, 1)
TABLE = "raw.fevm_eth_logs"


def build_url(day: dt.date) -> str:
    return f"{BASE_URL}/{day:%Y/%m/%d}/eth_getBlockReceipts.v1.r1.ndjson.brotli"


def daily_logs_select(url: str, day: dt.date) -> str:
    return f"""
        with receipts as (
            select unnest(result) as receipt
            from read_ndjson_auto('{url}')
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


def date_range(start: dt.date, end: dt.date) -> list[dt.date]:
    days = []
    day = start
    while day <= end:
        days.append(day)
        day += dt.timedelta(days=1)
    return days


def loaded_dates() -> set[dt.date] | None:
    with fdp.db_connection() as conn:
        if not table_exists(conn, "raw", "fevm_eth_logs"):
            return None
        rows = conn.execute(f"select distinct file_date from {TABLE}").fetchall()
    return {row[0] for row in rows}


def eth_logs() -> None:
    latest_day = dt.datetime.now(dt.UTC).date() - dt.timedelta(days=1)
    if latest_day < START_DATE:
        return

    loaded = loaded_dates()
    loaded_set = loaded or set()
    pending = [
        day for day in date_range(START_DATE, latest_day) if day not in loaded_set
    ]
    if not pending:
        return

    with fdp.db_connection() as conn:
        conn.execute("create schema if not exists raw")
        conn.execute("install httpfs; load httpfs")
        has_table = loaded is not None

        with httpx.Client(follow_redirects=True, timeout=10) as client:
            for day in pending:
                url = build_url(day)
                resp = client.head(url)
                if resp.status_code == 404:
                    continue
                resp.raise_for_status()

                select_sql = daily_logs_select(url, day)
                if has_table:
                    conn.execute(f"insert into {TABLE} {select_sql}")
                else:
                    conn.execute(f"create table {TABLE} as {select_sql}")
                    has_table = True
