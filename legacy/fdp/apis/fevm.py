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
ABI_LOAD_MAX_ATTEMPTS = 3
DECODE_CHUNK_SIZE = 50_000
MAX_DECODE_ERROR_LOGS = 20
DECODED_LOG_COLUMNS = pd.Index(
    [
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
)
DECODED_LOGS_FROM_DF_SQL = """
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
ABI_REGISTRY = [
    {
        "name": "filecoin_pay_v1",
        "abi_url": "https://raw.githubusercontent.com/FilOzone/filecoin-services/refs/heads/main/service_contracts/abi/FilecoinPayV1.abi.json",
        "related_contracts": [
            "0x23b1e018f08bb982348b15a86ee926eebf7f4daa",
        ],
    },
    {
        "name": "pdp_verifier",
        "abi_url": "https://raw.githubusercontent.com/FilOzone/filecoin-services/refs/heads/main/service_contracts/abi/PDPVerifier.abi.json",
        "related_contracts": [
            "0xbadd0b92c1c71d02e7d520f64c0876538fa2557f",
            "0xe2dc211bffca499761570e04e8143be2ba66095f",
        ],
    },
    {
        "name": "service_provider_registry",
        "abi_url": "https://raw.githubusercontent.com/FilOzone/filecoin-services/refs/heads/main/service_contracts/abi/ServiceProviderRegistry.abi.json",
        "related_contracts": [
            "0xf55ddbf63f1b55c3f1d4fa7e339a68ab7b64a5eb",
            "0xe255d3a89d6b326b48bc0fc94a472a839471d6b0",
        ],
    },
    {
        "name": "filecoin_warm_storage_service",
        "abi_url": "https://raw.githubusercontent.com/FilOzone/filecoin-services/refs/heads/main/service_contracts/abi/FilecoinWarmStorageService.abi.json",
        "related_contracts": [
            "0x8408502033c418e1bbc97ce9ac48e5528f371a9f",
            "0xd60b90f6d3c42b26a246e141ec701a20dde2fa61",
        ],
    },
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
    context: dg.AssetExecutionContext | None = None,
    *,
    max_attempts: int = ABI_LOAD_MAX_ATTEMPTS,
) -> tuple[dict[str, list[EventDecoder]], list[str]]:
    event_map: dict[str, list[EventDecoder]] = {}
    failed_abis: list[str] = []

    for entry in registry:
        name = entry["name"]
        abi_url = entry["abi_url"]
        related_contracts = (
            entry.get("related_contracts") or entry.get("addresses") or None
        )
        address_set = (
            {addr.lower() for addr in related_contracts} if related_contracts else None
        )

        abi: list[dict[str, Any]] | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                abi = _load_abi(abi_url)
                break
            except Exception as exc:
                if context is not None:
                    context.log.warning(
                        f"Failed to load ABI {name} from {abi_url} "
                        f"(attempt {attempt}/{max_attempts}): "
                        f"{type(exc).__name__}: {exc}"
                    )

        if abi is None:
            failed_abis.append(name)
            continue

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

    return event_map, failed_abis


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


def _stringify_log_value(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, (bytes, bytearray, HexBytes)):
        return "0x" + HexBytes(value).hex()
    return str(value)


def _format_row_context(row: dict[str, Any]) -> str:
    topics = _coerce_topics(row.get("topics"))
    topic0 = _topic0_from_value(topics[0]) if topics else "None"
    return (
        f"file_date={row.get('file_date')} "
        f"address={row.get('address')} "
        f"transaction_hash={_stringify_log_value(row.get('transactionHash'))} "
        f"log_index={row.get('logIndex')} "
        f"topic0={topic0}"
    )


def _coerce_date(value: Any) -> datetime.date | None:
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    return datetime.date.fromisoformat(str(value))


def _table_exists(conn: Any, table_name: str) -> bool:
    return (
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


def _max_file_date(conn: Any, table_name: str) -> datetime.date | None:
    if not _table_exists(conn, table_name):
        return None
    max_file_date = conn.execute(
        f'select cast(max(file_date) as date) from raw."{table_name}"'
    ).fetchone()[0]
    return _coerce_date(max_file_date)


def _next_day_to_process(
    conn: Any,
    table_name: str,
    start_day: datetime.date,
) -> datetime.date:
    last_day = _max_file_date(conn, table_name)
    if last_day is None:
        return start_day
    return last_day + datetime.timedelta(days=1)


def _iter_days(
    start_day: datetime.date,
    end_day: datetime.date,
) -> list[datetime.date]:
    day_count = (end_day - start_day).days + 1
    return [start_day + datetime.timedelta(days=offset) for offset in range(day_count)]


def _create_decoded_logs_table(conn: Any, table_name: str) -> None:
    conn.execute(f"drop table if exists raw.{table_name}")
    conn.execute(
        f"""
        create table raw.{table_name} (
            address varchar,
            block_number bigint,
            log_index bigint,
            transaction_hash varchar,
            transaction_index bigint,
            topic0 varchar,
            event_name varchar,
            abi_name varchar,
            args json,
            file_date timestamp
        )
        """
    )


@dg.asset(compute_kind="python")
def raw_ribrpc_eth_logs(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    table_name = context.asset_key.to_user_string()

    with duckdb.get_connection() as conn:
        conn.execute("install httpfs")
        conn.execute("load httpfs")

        table_exists = _table_exists(conn, table_name)
        from_day = _next_day_to_process(conn, table_name, START_DATE)
        to_day = datetime.date.today()
        if from_day > to_day:
            context.log.info("Data is up to date.")
            return dg.MaterializeResult()

        for day in _iter_days(from_day, to_day):
            url = _build_url(day)
            response = httpx.head(url, follow_redirects=True, timeout=10)
            if response.status_code == 404:
                context.log.warning(f"Missing logs for {day:%Y-%m-%d}. Skipping {url}")
                continue
            response.raise_for_status()

            context.log.info(f"Loading {url}")
            select_sql = _select_sql(url, day)
            if not table_exists:
                conn.execute(f"create table raw.{table_name} as {select_sql}")
                table_exists = True
            else:
                conn.execute(f"insert into raw.{table_name} {select_sql}")

    return dg.MaterializeResult()


@dg.asset(compute_kind="python", deps=[raw_ribrpc_eth_logs])
def raw_ribrpc_eth_logs_decoded(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
) -> dg.MaterializeResult:
    table_name = context.asset_key.to_user_string()
    event_map, failed_abis = _build_event_map(ABI_REGISTRY, context)
    if failed_abis:
        context.log.warning(
            "Failed to load one or more ABIs; leaving decoded table unchanged to "
            f"avoid publishing partial data. failed_abis={failed_abis}"
        )
        return dg.MaterializeResult(
            metadata={
                "dagster/row_count": 0,
                "failed_abis": ", ".join(failed_abis),
            }
        )

    web3 = Web3()
    decode_error_count = 0
    decoded_count = 0
    hard_error_count = 0
    processed_day_count = 0
    skipped_day_count = 0
    staging_table_name = f"{table_name}__staging"

    with duckdb.get_connection() as conn:
        if not _table_exists(conn, table_name):
            _create_decoded_logs_table(conn, table_name)

        from_day = _next_day_to_process(conn, table_name, START_DATE)
        to_day = _max_file_date(conn, "raw_ribrpc_eth_logs")
        if to_day is None or from_day > to_day:
            context.log.info("Decoded FEVM logs are up to date.")
            return dg.MaterializeResult(
                metadata={
                    "dagster/row_count": 0,
                    "decode_errors": 0,
                    "hard_errors": 0,
                    "processed_days": 0,
                    "skipped_days": 0,
                }
            )

        _create_decoded_logs_table(conn, staging_table_name)

        try:
            for day in _iter_days(from_day, to_day):
                context.log.info(f"Decoding FEVM log day {day}.")
                conn.execute(f"delete from raw.{staging_table_name}")

                day_decode_error_count = 0
                day_decoded_count = 0
                day_failed = False
                day_row_count = conn.execute(
                    """
                    select count(*)
                    from raw.raw_ribrpc_eth_logs
                    where cast(file_date as date) = ?
                    """,
                    [day],
                ).fetchone()[0]
                day_row_count = int(day_row_count)

                for offset in range(0, day_row_count, DECODE_CHUNK_SIZE):
                    try:
                        raw_df = conn.execute(
                            """
                            select *
                            from raw.raw_ribrpc_eth_logs
                            where cast(file_date as date) = ?
                            limit ? offset ?
                            """,
                            [day, DECODE_CHUNK_SIZE, offset],
                        ).df()
                    except Exception as exc:
                        hard_error_count += 1
                        day_failed = True
                        context.log.error(
                            f"Failed to load raw chunk for day={day} offset={offset}: "
                            f"{type(exc).__name__}: {exc}"
                        )
                        break

                    if raw_df.empty:
                        continue

                    chunk_decode_error_count = 0
                    decoded_rows: list[dict[str, Any]] = []
                    columns = list(raw_df.columns)
                    for row_index, row in enumerate(
                        raw_df.itertuples(index=False, name=None),
                        start=offset,
                    ):
                        entry = dict(zip(columns, row))
                        try:
                            decoded = _decode_row(web3, entry, event_map)
                        except Exception as exc:
                            decode_error_count += 1
                            day_decode_error_count += 1
                            chunk_decode_error_count += 1
                            if decode_error_count <= MAX_DECODE_ERROR_LOGS:
                                context.log.warning(
                                    f"Skipping undecodable log for day={day} row={row_index}: "
                                    f"{_format_row_context(entry)}; "
                                    f"{type(exc).__name__}: {exc}"
                                )
                            elif decode_error_count == MAX_DECODE_ERROR_LOGS + 1:
                                context.log.warning(
                                    "Reached decode error log limit; suppressing "
                                    "additional per-row warnings."
                                )
                            continue

                        if decoded:
                            decoded_rows.append(decoded)

                    if chunk_decode_error_count:
                        context.log.warning(
                            f"Skipped {chunk_decode_error_count} undecodable logs "
                            f"for day={day} in chunk offset={offset}."
                        )

                    if not decoded_rows:
                        continue

                    df = pd.DataFrame(decoded_rows, columns=DECODED_LOG_COLUMNS)
                    try:
                        conn.sql(
                            f"insert into raw.{staging_table_name} {DECODED_LOGS_FROM_DF_SQL}"
                        )
                    except Exception as exc:
                        hard_error_count += 1
                        day_failed = True
                        context.log.error(
                            f"Failed to write decoded chunk for day={day} offset={offset}: "
                            f"{type(exc).__name__}: {exc}"
                        )
                        break
                    day_decoded_count += df.shape[0]
                    decoded_count += df.shape[0]

                if day_failed:
                    skipped_day_count += 1
                    conn.execute(f"delete from raw.{staging_table_name}")
                    context.log.warning(
                        f"Failed to fully decode day={day}; leaving it for a future retry."
                    )
                    continue

                try:
                    conn.execute(
                        f"insert into raw.{table_name} "
                        f"select * from raw.{staging_table_name}"
                    )
                except Exception as exc:
                    hard_error_count += 1
                    skipped_day_count += 1
                    conn.execute(f"delete from raw.{staging_table_name}")
                    context.log.error(
                        f"Failed to publish decoded rows for day={day}: "
                        f"{type(exc).__name__}: {exc}"
                    )
                    continue

                conn.execute(f"delete from raw.{staging_table_name}")
                processed_day_count += 1
                context.log.info(
                    f"Processed day={day} decoded_rows={day_decoded_count} "
                    f"decode_errors={day_decode_error_count}."
                )
        finally:
            conn.execute(f"drop table if exists raw.{staging_table_name}")

    return dg.MaterializeResult(
        metadata={
            "dagster/row_count": decoded_count,
            "decode_errors": decode_error_count,
            "hard_errors": hard_error_count,
            "processed_days": processed_day_count,
            "skipped_days": skipped_day_count,
        }
    )
