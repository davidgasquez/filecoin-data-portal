# asset.description = Current storage provider state from Filecoin JSON-RPC snapshots.

# asset.depends = model.storage_provider_power_daily
# asset.depends = model.storage_provider_sector_lifecycle_daily
# asset.depends = model.storage_provider_block_rewards_daily
# asset.depends = model.verified_claims

# asset.materialization = dataframe

# asset.column = provider_id | Filecoin storage provider actor id address.
# asset.column = owner_id | Current owner actor id address.
# asset.column = worker_id | Current worker actor id address.
# asset.column = beneficiary_id | Current beneficiary actor id address.
# asset.column = peer_id | Current libp2p peer id.
# asset.column = control_addresses | Current JSON array of control addresses.
# asset.column = multi_addresses | Current JSON array of multiaddrs.
# asset.column = sector_size | Current sector size in bytes.
# asset.column = live_sectors | Current live sector count.
# asset.column = active_sectors | Current active sector count.
# asset.column = faulty_sectors | Current faulty sector count.
# asset.column = actor_balance_fil | Current miner actor balance in FIL.
# asset.column = available_balance_fil | Current available miner balance in FIL.
# asset.column = market_escrow_fil | Current market escrow balance in FIL.
# asset.column = market_locked_fil | Current market locked balance in FIL.
# asset.column = market_available_fil | Current market available balance in FIL.
# asset.column = initial_pledge_fil | Current initial pledge in FIL.
# asset.column = locked_funds_fil | Current locked funds in FIL.
# asset.column = pre_commit_deposits_fil | Current pre-commit deposits in FIL.
# asset.column = fee_debt_fil | Current fee debt in FIL.
# asset.column = fetched_at | Snapshot fetch timestamp.

# asset.not_null = provider_id
# asset.not_null = sector_size
# asset.unique = provider_id
# asset.assert = sector_size > 0

import asyncio
import base64
import datetime as dt
import json
import os
import random
from decimal import Decimal
from itertools import batched
from json import JSONDecodeError
from typing import Any

import httpx
import polars as pl
from httpx import HTTPStatusError, TimeoutException, TransportError
from multiaddr import Multiaddr

import fdp


def env_int(name: str, default: int) -> int:
    value = int(os.getenv(name, str(default)))
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def env_float(name: str, default: float) -> float:
    value = float(os.getenv(name, str(default)))
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


DEFAULT_RPC_URLS = (
    "https://filecoin.chainup.net/rpc/v1",
    "https://api.node.glif.io/rpc/v1",
    "https://api.chain.love/rpc/v1",
)
CONFIGURED_RPC_URLS = tuple(
    url.strip()
    for url in os.getenv("FDP_FILECOIN_RPC_URLS", ",".join(DEFAULT_RPC_URLS)).split(",")
    if url.strip()
)
RPC_URLS = CONFIGURED_RPC_URLS or DEFAULT_RPC_URLS
BATCH_SIZE = env_int("FDP_FILECOIN_RPC_BATCH_SIZE", 10)
MAX_CONCURRENT = env_int("FDP_FILECOIN_RPC_MAX_CONCURRENT", 2)
REQUEST_TIMEOUT_SECONDS = env_float("FDP_FILECOIN_RPC_TIMEOUT_SECONDS", 45)
MAX_RPC_ATTEMPTS = env_int("FDP_FILECOIN_RPC_MAX_ATTEMPTS", 5)
BASE_RETRY_SECONDS = env_float("FDP_FILECOIN_RPC_BASE_RETRY_SECONDS", 2)
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
RETRYABLE_RPC_ERROR_CODES = {-32601, -32160, -32090, -32062}
ATTO_FIL = Decimal("1000000000000000000")
RPC_METHODS = {
    "info": "Filecoin.StateMinerInfo",
    "sector_count": "Filecoin.StateMinerSectorCount",
    "market_balance": "Filecoin.StateMarketBalance",
    "state": "Filecoin.StateReadState",
}

SCHEMA = {
    "provider_id": pl.String,
    "owner_id": pl.String,
    "worker_id": pl.String,
    "beneficiary_id": pl.String,
    "peer_id": pl.String,
    "control_addresses": pl.String,
    "multi_addresses": pl.String,
    "sector_size": pl.Int64,
    "live_sectors": pl.Int64,
    "active_sectors": pl.Int64,
    "faulty_sectors": pl.Int64,
    "actor_balance_fil": pl.Float64,
    "available_balance_fil": pl.Float64,
    "market_escrow_fil": pl.Float64,
    "market_locked_fil": pl.Float64,
    "market_available_fil": pl.Float64,
    "initial_pledge_fil": pl.Float64,
    "locked_funds_fil": pl.Float64,
    "pre_commit_deposits_fil": pl.Float64,
    "fee_debt_fil": pl.Float64,
    "fetched_at": pl.Datetime,
}


def current_info() -> pl.DataFrame:
    rows = asyncio.run(load_rows())
    return pl.DataFrame(rows, schema_overrides=SCHEMA).sort("provider_id")


async def load_rows() -> list[dict[str, Any]]:
    fetched_at = dt.datetime.now(dt.UTC).replace(tzinfo=None)
    provider_ids = load_provider_ids()
    limits = httpx.Limits(
        max_connections=MAX_CONCURRENT, max_keepalive_connections=MAX_CONCURRENT
    )

    timeout = httpx.Timeout(
        REQUEST_TIMEOUT_SECONDS,
        pool=REQUEST_TIMEOUT_SECONDS * MAX_CONCURRENT,
    )
    async with httpx.AsyncClient(
        follow_redirects=True, timeout=timeout, limits=limits
    ) as client:
        tipset_key = await fetch_tipset_key(client)
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)

        async def fetch(index: int, chunk: tuple[str, ...]) -> list[dict[str, Any]]:
            async with semaphore:
                return await fetch_chunk(
                    client,
                    chunk,
                    tipset_key,
                    fetched_at,
                    rpc_urls_for(index),
                )

        chunks = tuple(batched(provider_ids, BATCH_SIZE, strict=False))
        results = await asyncio.gather(
            *(fetch(index, chunk) for index, chunk in enumerate(chunks))
        )
        return [row for chunk in results for row in chunk]


def load_provider_ids() -> list[str]:
    query = """
        select provider_id from model.storage_provider_sector_lifecycle_daily
        union
        select provider_id from model.storage_provider_power_daily
        union
        select provider_id from model.storage_provider_block_rewards_daily
        union
        select provider_id from model.verified_claims
        order by provider_id
    """
    with fdp.db_connection(read_only=True) as conn:
        return [pid for (pid,) in conn.execute(query).fetchall()]


async def fetch_tipset_key(client: httpx.AsyncClient) -> list[dict[str, str]]:
    response = await post_rpc(
        client,
        {"jsonrpc": "2.0", "id": 1, "method": "Filecoin.ChainHead", "params": []},
    )
    return response["result"]["Cids"]


async def fetch_chunk(
    client: httpx.AsyncClient,
    provider_ids: tuple[str, ...],
    tipset_key: list[dict[str, str]],
    fetched_at: dt.datetime,
    rpc_urls: tuple[str, ...],
) -> list[dict[str, Any]]:
    payload = [
        {
            "jsonrpc": "2.0",
            "id": f"{provider_id}:{alias}",
            "method": method,
            "params": [provider_id, tipset_key],
        }
        for provider_id in provider_ids
        for alias, method in RPC_METHODS.items()
    ]
    responses = await post_rpc(client, payload, rpc_urls)

    results: dict[str, dict[str, Any]] = {pid: {} for pid in provider_ids}
    for response in responses:
        provider_id, alias = response["id"].split(":", 1)
        if response.get("error"):
            raise ValueError(
                f"JSON-RPC error for {provider_id} {alias}: {response['error']}"
            )
        results[provider_id][alias] = response["result"]

    missing = [
        f"{provider_id}:{alias}"
        for provider_id in provider_ids
        for alias in RPC_METHODS
        if alias not in results[provider_id]
    ]
    if missing:
        raise ValueError(f"Missing JSON-RPC responses: {', '.join(missing[:5])}")

    return [build_row(pid, results[pid], fetched_at) for pid in provider_ids]


def build_row(
    provider_id: str, results: dict[str, Any], fetched_at: dt.datetime
) -> dict[str, Any]:
    info = results["info"]
    sector_count = results["sector_count"]
    market = results["market_balance"]
    state_result = results["state"]
    state = state_result.get("State")
    if not isinstance(state, dict):
        raise ValueError(f"Missing miner state for {provider_id}")

    escrow = atto_to_fil(market.get("Escrow"))
    locked = atto_to_fil(market.get("Locked"))
    available = escrow - locked if escrow is not None and locked is not None else None

    return {
        "provider_id": provider_id,
        "owner_id": null_if_empty(info.get("Owner")),
        "worker_id": null_if_empty(info.get("Worker")),
        "beneficiary_id": null_if_empty(info.get("Beneficiary")),
        "peer_id": null_if_empty(info.get("PeerId")),
        "control_addresses": json_array(info.get("ControlAddresses")),
        "multi_addresses": json_array(decode_multiaddrs(info.get("Multiaddrs"))),
        "sector_size": info.get("SectorSize"),
        "live_sectors": sector_count.get("Live"),
        "active_sectors": sector_count.get("Active"),
        "faulty_sectors": sector_count.get("Faulty"),
        "actor_balance_fil": atto_to_fil(state_result.get("Balance")),
        "available_balance_fil": miner_available_balance_fil(state_result),
        "market_escrow_fil": escrow,
        "market_locked_fil": locked,
        "market_available_fil": available,
        "initial_pledge_fil": atto_to_fil(state.get("InitialPledge")),
        "locked_funds_fil": atto_to_fil(state.get("LockedFunds")),
        "pre_commit_deposits_fil": atto_to_fil(state.get("PreCommitDeposits")),
        "fee_debt_fil": atto_to_fil(state.get("FeeDebt")),
        "fetched_at": fetched_at,
    }


async def post_rpc(
    client: httpx.AsyncClient,
    payload: Any,
    rpc_urls: tuple[str, ...] | None = None,
) -> Any:
    urls = RPC_URLS if rpc_urls is None else rpc_urls
    last_error: Exception | None = None

    for attempt in range(1, MAX_RPC_ATTEMPTS + 1):
        for url in urls:
            try:
                return await try_rpc_url(client, url, payload)
            except (
                HTTPStatusError,
                TimeoutException,
                TransportError,
                JSONDecodeError,
                RetryableRpcError,
            ) as exc:
                last_error = exc

        if attempt < MAX_RPC_ATTEMPTS:
            await asyncio.sleep(retry_delay(last_error, attempt))

    raise RuntimeError(
        f"JSON-RPC request failed after {MAX_RPC_ATTEMPTS} attempts "
        f"across {len(urls)} URLs: {last_error!r}"
    ) from last_error


async def try_rpc_url(client: httpx.AsyncClient, url: str, payload: Any) -> Any:
    response = await client.post(url, json=payload)
    if response.status_code in RETRYABLE_STATUS_CODES:
        response.raise_for_status()
    response.raise_for_status()
    data = parse_rpc_json(response)
    raise_if_retryable_rpc_error(data)
    return data


def rpc_urls_for(index: int) -> tuple[str, ...]:
    offset = index % len(RPC_URLS)
    return (*RPC_URLS[offset:], *RPC_URLS[:offset])


class RetryableRpcError(Exception):
    pass


def retry_delay(error: Exception | None, attempt: int) -> float:
    if isinstance(error, HTTPStatusError):
        retry_after = error.response.headers.get("retry-after")
        if retry_after is not None:
            try:
                return float(retry_after)
            except ValueError:
                pass
    return BASE_RETRY_SECONDS * (2 ** (attempt - 1)) + random.uniform(0, 1)


def raise_if_retryable_rpc_error(data: Any) -> None:
    responses = data if isinstance(data, list) else [data]
    for response in responses:
        if not isinstance(response, dict) or not isinstance(
            error := response.get("error"), dict
        ):
            continue
        message = str(error.get("message", "")).lower()
        if error.get("code") in RETRYABLE_RPC_ERROR_CODES or any(
            phrase in message for phrase in ("rate limit", "too many requests")
        ):
            raise RetryableRpcError(error)


def miner_available_balance_fil(state_result: dict[str, Any]) -> float | None:
    balance = atto_decimal(state_result.get("Balance"))
    if balance is None:
        return None

    state = state_result.get("State") or {}
    locked = sum(
        atto_decimal(state.get(field)) or Decimal(0)
        for field in (
            "InitialPledge",
            "LockedFunds",
            "PreCommitDeposits",
            "FeeDebt",
        )
    )
    available = max(balance - locked, Decimal(0))
    return float(available / ATTO_FIL)


def parse_rpc_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except JSONDecodeError:
        text = response.text.lstrip()
        decoder = json.JSONDecoder()
        data, _ = decoder.raw_decode(text)
        return data


def atto_to_fil(value: Any) -> float | None:
    value_atto = atto_decimal(value)
    return float(value_atto / ATTO_FIL) if value_atto is not None else None


def atto_decimal(value: Any) -> Decimal | None:
    cleaned = null_if_empty(value)
    return Decimal(cleaned) if cleaned else None


def decode_multiaddrs(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [
        str(Multiaddr(base64.b64decode(s))) for v in value if (s := null_if_empty(v))
    ]


def json_array(value: Any) -> str | None:
    if not isinstance(value, list):
        return None
    items = [s for v in value if (s := null_if_empty(v))]
    return json.dumps(items) if items else None


def null_if_empty(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return None if not s or s == "<empty>" else s
