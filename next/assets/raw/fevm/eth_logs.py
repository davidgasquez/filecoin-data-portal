# asset.description = Raw eth logs from Rib RPC archive.
# asset.materialization = custom

# asset.column = address | Contract address that emitted the log.
# asset.column = blockHash | Hash of the block containing the log.
# asset.column = blockNumber | Block number as returned by the archive source in hex.
# asset.column = data | Hex-encoded non-indexed event payload.
# asset.column = logIndex | Log position within the block, as returned in hex.
# asset.column = removed | Whether the log was removed by a chain reorg.
# asset.column = topics | Indexed log topics as an array of hex strings.
# asset.column = transactionHash | Hash of the transaction that emitted the log.
# asset.column = transactionIndex | Transaction index within the block in hex.
# asset.column = file_date | Archive partition date used to load this row.

import datetime as dt

import httpx

import fdp

BASE_URL = "https://ribrpc.fil.st/archive/fil/mainnet"
START_DATE = dt.date(2025, 10, 1)
TABLE = "raw.fevm_eth_logs"


def build_url(day: dt.date) -> str:
    return f"{BASE_URL}/{day:%Y/%m/%d}/eth_getLogs.v1.r1.flattened.ndjson.zst"


def last_loaded_date() -> dt.date | None:
    with fdp.db_connection() as conn:
        row = conn.execute(
            """
            select 1
            from information_schema.tables
            where table_schema = 'raw' and table_name = 'fevm_eth_logs'
            """
        ).fetchone()
        if row is None:
            return None
        result = conn.execute(f"select max(file_date) from {TABLE}").fetchone()
        return result[0] if result and result[0] else None


def eth_logs() -> None:
    last = last_loaded_date()
    from_day = last + dt.timedelta(days=1) if last else START_DATE

    today = dt.date.today()
    if from_day > today:
        return

    with fdp.db_connection() as conn:
        conn.execute("create schema if not exists raw")
        conn.execute("install httpfs; load httpfs")
        table_exists = last is not None

        with httpx.Client(follow_redirects=True, timeout=10) as client:
            day = from_day
            while day <= today:
                url = build_url(day)
                resp = client.head(url)
                if resp.status_code == 404:
                    day += dt.timedelta(days=1)
                    continue
                resp.raise_for_status()

                select_sql = (
                    f"select *, date '{day}' as file_date "
                    f"from read_ndjson_auto('{url}', compression='zstd')"
                )
                if table_exists:
                    conn.execute(f"insert into {TABLE} {select_sql}")
                else:
                    conn.execute(f"create table {TABLE} as {select_sql}")
                    table_exists = True

                day += dt.timedelta(days=1)
