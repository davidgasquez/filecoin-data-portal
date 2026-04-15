# asset.description = Decoded events for selected FEVM contracts from raw eth logs.

# asset.materialization = custom

# asset.depends = raw.fevm_contract_registry
# asset.depends = raw.fevm_eth_logs

# asset.column = address | Contract address that emitted the decoded event.
# asset.column = block_number | Decoded block number as an integer.
# asset.column = log_index | Decoded log index within the block.
# asset.column = transaction_hash | Transaction hash that emitted the event.
# asset.column = transaction_index | Decoded transaction index within the block.
# asset.column = topic0 | Primary event signature topic used for ABI lookup.
# asset.column = event_name | Decoded ABI event name.
# asset.column = abi_name | Logical ABI source used to decode the event.
# asset.column = args | Decoded event arguments stored as JSON.
# asset.column = file_date | Archive partition date of the raw log.

import datetime as dt
import json
from dataclasses import dataclass
from typing import Any

import polars as pl
from eth_utils import keccak
from hexbytes import HexBytes
from web3 import Web3

import fdp
from fdp.api import table_exists

TABLE_NAME = "raw.fevm_eth_logs_decoded"
OUTPUT_SCHEMA = {
    "address": pl.String,
    "block_number": pl.Int64,
    "log_index": pl.Int64,
    "transaction_hash": pl.String,
    "transaction_index": pl.Int64,
    "topic0": pl.String,
    "event_name": pl.String,
    "abi_name": pl.String,
    "args_json": pl.String,
    "file_date": pl.Date,
}
ABI_CODEC = Web3().codec


@dataclass(frozen=True)
class EventField:
    name: str
    abi_type: str
    indexed: bool
    is_dynamic: bool


@dataclass(frozen=True)
class EventSpec:
    abi_name: str
    event_name: str
    address: str
    topic0: str
    indexed_fields: tuple[EventField, ...]
    data_fields: tuple[EventField, ...]


def pending_dates() -> list[dt.date]:
    with fdp.db_connection() as conn:
        if not table_exists(conn, "raw", "fevm_eth_logs_decoded"):
            rows = conn.execute(
                """
                select distinct file_date
                from raw.fevm_eth_logs
                order by 1
                """
            ).fetchall()
        else:
            rows = conn.execute(
                f"""
                select distinct raw.file_date
                from raw.fevm_eth_logs as raw
                where not exists (
                    select 1
                    from {TABLE_NAME} as decoded
                    where decoded.file_date = raw.file_date
                )
                order by 1
                """
            ).fetchall()
    return [row[0] for row in rows]


def canonical_abi_type(parameter: dict[str, Any]) -> str:
    type_name = str(parameter["type"])
    if not type_name.startswith("tuple"):
        return type_name

    components = ",".join(
        canonical_abi_type(component) for component in parameter.get("components", [])
    )
    suffix = type_name.removeprefix("tuple")
    return f"({components}){suffix}"


def is_dynamic_abi_type(parameter: dict[str, Any]) -> bool:
    type_name = str(parameter["type"])
    if type_name in {"string", "bytes"}:
        return True
    if "[" in type_name:
        return True
    if not type_name.startswith("tuple"):
        return False
    return any(
        is_dynamic_abi_type(component) for component in parameter.get("components", [])
    )


def build_event_field(parameter: dict[str, Any]) -> EventField:
    name = str(parameter.get("name") or "")
    return EventField(
        name=name,
        abi_type=canonical_abi_type(parameter),
        indexed=bool(parameter.get("indexed")),
        is_dynamic=is_dynamic_abi_type(parameter),
    )


def event_topic0(event_abi: dict[str, Any]) -> str:
    field_types = ",".join(
        canonical_abi_type(parameter) for parameter in event_abi["inputs"]
    )
    signature = f"{event_abi['name']}({field_types})"
    return "0x" + keccak(text=signature).hex()


def build_event_spec(
    abi_name: str,
    address: str,
    event_abi: dict[str, Any],
) -> EventSpec:
    fields = tuple(build_event_field(parameter) for parameter in event_abi["inputs"])
    return EventSpec(
        abi_name=abi_name,
        event_name=str(event_abi["name"]),
        address=address,
        topic0=event_topic0(event_abi),
        indexed_fields=tuple(field for field in fields if field.indexed),
        data_fields=tuple(field for field in fields if not field.indexed),
    )


def load_event_specs() -> dict[tuple[str, str], EventSpec]:
    with fdp.db_connection() as conn:
        rows = conn.execute(
            """
            select contract_name, lower(address) as address, abi_json
            from raw.fevm_contract_registry
            order by contract_name, address
            """
        ).fetchall()

    specs: dict[tuple[str, str], EventSpec] = {}
    for contract_name, address, abi_json in rows:
        abi = json.loads(abi_json)
        if not isinstance(abi, list):
            raise TypeError(f"ABI for {contract_name} at {address} must be a list")

        for entry in abi:
            if entry.get("type") != "event" or entry.get("anonymous"):
                continue
            spec = build_event_spec(str(contract_name), str(address), entry)
            key = (spec.address, spec.topic0)
            if key in specs:
                raise ValueError(
                    f"Duplicate event decoder for {spec.address} {spec.topic0}"
                )
            specs[key] = spec
    return specs


def sql_string_list(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{value}'" for value in values)


def fetch_candidate_rows(
    file_date: dt.date,
    addresses_sql: str,
    topic0s_sql: str,
) -> list[tuple[Any, ...]]:
    with fdp.db_connection() as conn:
        return conn.execute(
            f"""
            select
                lower(address) as address,
                blockNumber,
                data,
                logIndex,
                topics,
                transactionHash,
                transactionIndex,
                file_date
            from raw.fevm_eth_logs
            where file_date = ?
              and lower(address) in ({addresses_sql})
              and array_length(topics) > 0
              and lower(topics[1]) in ({topic0s_sql})
            order by blockNumber, logIndex
            """,
            [file_date],
        ).fetchall()


def parse_hex_int(value: str | int) -> int:
    if isinstance(value, int):
        return value
    return int(value, 16) if value.startswith("0x") else int(value)


def normalize_value(value: Any) -> Any:
    if isinstance(value, (HexBytes, bytes, bytearray)):
        return "0x" + HexBytes(value).hex()
    if isinstance(value, list | tuple):
        return [normalize_value(item) for item in value]
    return value


def decode_topic_value(field: EventField, topic_hex: str) -> Any:
    if field.is_dynamic:
        return topic_hex.lower()
    return normalize_value(ABI_CODEC.decode([field.abi_type], HexBytes(topic_hex))[0])


def decode_data_values(fields: tuple[EventField, ...], data_hex: str) -> dict[str, Any]:
    if not fields:
        return {}

    values = ABI_CODEC.decode(
        [field.abi_type for field in fields],
        HexBytes(data_hex),
    )
    return {
        field.name: normalize_value(value)
        for field, value in zip(fields, values, strict=True)
    }


def decode_args(spec: EventSpec, topics: list[str], data_hex: str) -> dict[str, Any]:
    expected_topic_count = 1 + len(spec.indexed_fields)
    if len(topics) != expected_topic_count:
        raise ValueError(
            f"Unexpected topic count for {spec.abi_name}.{spec.event_name}: "
            f"expected {expected_topic_count}, got {len(topics)}"
        )

    args = {
        field.name: decode_topic_value(field, topic_hex)
        for field, topic_hex in zip(spec.indexed_fields, topics[1:], strict=True)
    }
    args.update(decode_data_values(spec.data_fields, data_hex))
    return args


def decode_row(
    row: tuple[Any, ...],
    event_specs: dict[tuple[str, str], EventSpec],
) -> dict[str, Any] | None:
    (
        address,
        block_number_hex,
        data_hex,
        log_index_hex,
        topics,
        transaction_hash_hex,
        transaction_index_hex,
        file_date,
    ) = row

    topic0 = str(topics[0]).lower()
    spec = event_specs.get((str(address), topic0))
    if spec is None:
        return None

    block_number = parse_hex_int(str(block_number_hex))
    log_index = parse_hex_int(str(log_index_hex))
    transaction_index = parse_hex_int(str(transaction_index_hex))
    args = decode_args(spec, [str(topic) for topic in topics], str(data_hex))

    return {
        "address": str(address),
        "block_number": block_number,
        "log_index": log_index,
        "transaction_hash": "0x" + HexBytes(str(transaction_hash_hex)).hex(),
        "transaction_index": transaction_index,
        "topic0": topic0,
        "event_name": spec.event_name,
        "abi_name": spec.abi_name,
        "args_json": json.dumps(args, sort_keys=True),
        "file_date": file_date,
    }


def ensure_table() -> None:
    with fdp.db_connection() as conn:
        conn.execute("create schema if not exists raw")
        conn.execute(
            f"""
            create table if not exists {TABLE_NAME} (
                address varchar,
                block_number bigint,
                log_index bigint,
                transaction_hash varchar,
                transaction_index bigint,
                topic0 varchar,
                event_name varchar,
                abi_name varchar,
                args json,
                file_date date
            )
            """
        )


def insert_rows(rows: list[dict[str, Any]]) -> None:
    frame = pl.DataFrame(rows, schema=OUTPUT_SCHEMA)
    with fdp.db_connection() as conn:
        conn.register("decoded_rows", frame)
        conn.execute(
            f"""
            insert into {TABLE_NAME}
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
            from decoded_rows
            """
        )


def eth_logs_decoded() -> None:
    ensure_table()

    event_specs = load_event_specs()
    if not event_specs:
        return

    dates = pending_dates()
    if not dates:
        return

    addresses = tuple(sorted({address for address, _ in event_specs}))
    topic0s = tuple(sorted({topic0 for _, topic0 in event_specs}))
    addresses_sql = sql_string_list(addresses)
    topic0s_sql = sql_string_list(topic0s)

    for file_date in dates:
        decoded_rows = []
        for row in fetch_candidate_rows(file_date, addresses_sql, topic0s_sql):
            decoded = decode_row(row, event_specs)
            if decoded is not None:
                decoded_rows.append(decoded)
        if decoded_rows:
            insert_rows(decoded_rows)
