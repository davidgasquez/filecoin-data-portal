import datetime
import json
from dataclasses import dataclass
from typing import Any, cast

import dagster as dg
import httpx
import pandas as pd
from dagster_duckdb import DuckDBResource
from eth_typing import ABIEvent
from eth_utils.abi import event_abi_to_log_topic
from hexbytes import HexBytes
from web3 import Web3
from web3._utils.events import get_event_data
from web3.datastructures import AttributeDict

BASE_URL = "https://ribrpc.fil.st/archive/fil/mainnet"
START_DATE = datetime.date(2025, 10, 1)
ABI_REGISTRY = [
    {
        "name": "filecoin_pay_v1",
        "abi_url": "https://raw.githubusercontent.com/FilOzone/filecoin-services/refs/heads/main/service_contracts/abi/FilecoinPayV1.abi.json",
        "related_contracts": [
            "0x23b1e018f08bb982348b15a86ee926eebf7f4daa",
        ],
    }
]


@dataclass(frozen=True)
class EventDecoder:
    abi_name: str
    event_abi: dict[str, Any]
    addresses: set[str] | None


def _build_url(day: datetime.date) -> str:
    return f"{BASE_URL}/{day:%Y/%m/%d}/eth_getLogs.v1.r1.flattened.ndjson.zst"


def _select_sql(url: str, day: datetime.date) -> str:
    return (
        "select *, "
        f"date '{day:%Y-%m-%d}' as file_date "
        f"from read_ndjson_auto('{url}', compression='zstd')"
    )


def _parse_hex_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 16) if value.startswith("0x") else int(value)
    return int(value)


def _normalize(value: Any) -> Any:
    if isinstance(value, AttributeDict):
        return {key: _normalize(inner) for key, inner in value.items()}
    if isinstance(value, dict):
        return {key: _normalize(inner) for key, inner in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(inner) for inner in value]
    if isinstance(value, (HexBytes, bytes, bytearray)):
        return "0x" + HexBytes(value).hex()
    return value


def _load_abi(url: str) -> list[dict[str, Any]]:
    response = httpx.get(url, follow_redirects=True, timeout=15)
    response.raise_for_status()
    abi: list[dict[str, Any]] = response.json()
    return abi


def _build_event_map(
    registry: list[dict[str, Any]],
) -> dict[str, list[EventDecoder]]:
    event_map: dict[str, list[EventDecoder]] = {}
    for entry in registry:
        name = entry["name"]
        abi_url = entry["abi_url"]
        related_contracts = (
            entry.get("related_contracts") or entry.get("addresses") or None
        )
        address_set = (
            {addr.lower() for addr in related_contracts}
            if related_contracts
            else None
        )
        abi = _load_abi(abi_url)
        for abi_entry in abi:
            if abi_entry.get("type") != "event":
                continue
            topic = "0x" + event_abi_to_log_topic(cast(ABIEvent, abi_entry)).hex()
            event_map.setdefault(topic.lower(), []).append(
                EventDecoder(
                    abi_name=name,
                    event_abi=abi_entry,
                    addresses=address_set,
                )
            )
    return event_map


def _select_decoder(
    decoders: list[EventDecoder],
    address: str,
) -> EventDecoder | None:
    for decoder in decoders:
        if decoder.addresses and address in decoder.addresses:
            return decoder
    for decoder in decoders:
        if decoder.addresses is None:
            return decoder
    return None


def _topic0_from_value(value: Any) -> str:
    if isinstance(value, (bytes, bytearray, HexBytes)):
        return "0x" + HexBytes(value).hex()
    return str(value).lower()


def _coerce_topics(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if hasattr(value, "tolist"):
        return list(value.tolist())
    return [value]


def _log_from_row(row: dict[str, Any]) -> AttributeDict:
    topics = _coerce_topics(row.get("topics"))
    return AttributeDict(
        {
            "address": row["address"],
            "blockHash": HexBytes(row["blockHash"]),
            "blockNumber": _parse_hex_int(row["blockNumber"]),
            "data": HexBytes(row["data"]),
            "logIndex": _parse_hex_int(row["logIndex"]),
            "removed": bool(row["removed"]),
            "topics": [HexBytes(topic) for topic in topics],
            "transactionHash": HexBytes(row["transactionHash"]),
            "transactionIndex": _parse_hex_int(row["transactionIndex"]),
        }
    )


def _decode_row(
    web3: Web3,
    row: dict[str, Any],
    event_map: dict[str, list[EventDecoder]],
) -> dict[str, Any] | None:
    topics = _coerce_topics(row.get("topics"))
    if not topics:
        return None
    topic0 = _topic0_from_value(topics[0])
    decoders = event_map.get(topic0)
    if not decoders:
        return None

    log = _log_from_row(row)
    decoder = _select_decoder(decoders, log["address"].lower())
    if decoder is None:
        return None
    decoded = get_event_data(web3.codec, decoder.event_abi, log)

    args = {key: _normalize(value) for key, value in decoded["args"].items()}

    return {
        "address": log["address"],
        "block_number": log["blockNumber"],
        "log_index": log["logIndex"],
        "transaction_hash": "0x" + log["transactionHash"].hex(),
        "transaction_index": log["transactionIndex"],
        "topic0": topic0,
        "event_name": decoded["event"],
        "abi_name": decoder.abi_name,
        "args_json": json.dumps(args),
        "file_date": row["file_date"],
    }


@dg.asset(compute_kind="python")
def raw_ribrpc_eth_logs(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    table_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as conn:
        conn.execute("install httpfs")
        conn.execute("load httpfs")

        table_exists = (
            conn.execute(
                """
                select 1
                from information_schema.tables
                where table_schema = 'raw' and table_name = ?
                """,
                [table_name],
            ).fetchone()
            is not None
        )
        if table_exists:
            last_date = conn.execute(
                f'select max(file_date) from raw."{table_name}"'
            ).fetchone()[0]
        else:
            last_date = None

        if last_date:
            last_day = (
                last_date
                if isinstance(last_date, datetime.date)
                else datetime.date.fromisoformat(str(last_date))
            )
            from_day = last_day + datetime.timedelta(days=1)
        else:
            from_day = START_DATE

        to_day = datetime.date.today()
        if from_day > to_day:
            context.log.info(f"Data is up to date. Last update was on {from_day}")
            return dg.MaterializeResult()

        current = from_day
        while current <= to_day:
            url = _build_url(current)
            response = httpx.head(url, follow_redirects=True, timeout=10)
            if response.status_code == 404:
                context.log.warning(
                    f"Missing logs for {current:%Y-%m-%d}. Skipping {url}"
                )
                current += datetime.timedelta(days=1)
                continue
            response.raise_for_status()

            context.log.info(f"Loading {url}")
            select_sql = _select_sql(url, current)
            if not table_exists:
                conn.execute(f"create table raw.{table_name} as {select_sql}")
                table_exists = True
            else:
                conn.execute(f"insert into raw.{table_name} {select_sql}")
            current += datetime.timedelta(days=1)

    return dg.MaterializeResult()


@dg.asset(compute_kind="python", deps=[raw_ribrpc_eth_logs])
def raw_ribrpc_eth_logs_decoded(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    table_name = context.asset_key.to_user_string()
    event_map = _build_event_map(ABI_REGISTRY)
    web3 = Web3()
    output_columns: list[str] = [
        "address",
        "block_number",
        "log_index",
        "transaction_hash",
        "transaction_index",
        "topic0",
        "event_name",
        "abi_name",
        "args_json",
        "file_date",
    ]
    output_index = pd.Index(output_columns)
    chunk_size = 50_000
    decoded_count = 0
    table_initialized = False
    select_sql = """
    select
        address,
        block_number,
        log_index,
        transaction_hash,
        transaction_index,
        topic0,
        event_name,
        abi_name,
        cast(args_json as json) as args,
        file_date
    from df
    """

    with duckdb.get_connection() as conn:
        total_rows = conn.execute(
            "select count(*) from raw.raw_ribrpc_eth_logs"
        ).fetchone()[0]
        total_rows = int(total_rows)

        for offset in range(0, total_rows, chunk_size):
            raw_df = conn.execute(
                "select * from raw.raw_ribrpc_eth_logs limit ? offset ?",
                [chunk_size, offset],
            ).df()
            if raw_df.empty:
                continue

            decoded_rows: list[dict[str, Any]] = []
            columns = list(raw_df.columns)
            for row in raw_df.itertuples(index=False, name=None):
                entry = dict(zip(columns, row))
                decoded = _decode_row(web3, entry, event_map)
                if decoded:
                    decoded_rows.append(decoded)

            if not decoded_rows:
                continue

            df = pd.DataFrame(decoded_rows, columns=output_index)
            if not table_initialized:
                conn.sql(f"create or replace table raw.{table_name} as {select_sql}")
                table_initialized = True
            else:
                conn.sql(f"insert into raw.{table_name} {select_sql}")
            decoded_count += df.shape[0]

        if not table_initialized:
            df = pd.DataFrame(columns=output_index)
            conn.sql(f"create or replace table raw.{table_name} as {select_sql}")

    return dg.MaterializeResult(metadata={"dagster/row_count": decoded_count})
