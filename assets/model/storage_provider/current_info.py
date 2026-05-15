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
from decimal import Decimal
from typing import Any

import httpx
import polars as pl
from multiaddr import Multiaddr

import fdp

RPC_URL = "https://filecoin.chain.love/rpc"
BATCH_SIZE = 100
MAX_CONCURRENT_CHUNKS = 24
ATTO_FIL = Decimal("1000000000000000000")
RPC_METHODS = {
    "info": "Filecoin.StateMinerInfo",
    "sector_count": "Filecoin.StateMinerSectorCount",
    "market_balance": "Filecoin.StateMarketBalance",
    "available_balance": "Filecoin.StateMinerAvailableBalance",
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
    return build_dataframe(asyncio.run(load_current_info_rows()))


async def load_current_info_rows() -> list[dict[str, Any]]:
    provider_ids = load_provider_ids()
    fetched_at = dt.datetime.now(dt.UTC).replace(tzinfo=None)
    limits = httpx.Limits(
        max_connections=MAX_CONCURRENT_CHUNKS,
        max_keepalive_connections=MAX_CONCURRENT_CHUNKS,
    )

    rows: list[dict[str, Any]] = []
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=120,
        limits=limits,
    ) as client:
        tipset_key = await load_tipset_key(client)
        provider_chunks = chunked(provider_ids, BATCH_SIZE)

        for chunks in chunked(provider_chunks, MAX_CONCURRENT_CHUNKS):
            chunk_rows = await asyncio.gather(
                *(
                    fetch_chunk_rows(client, chunk, tipset_key, fetched_at)
                    for chunk in chunks
                )
            )
            rows.extend(row for chunk in chunk_rows for row in chunk)

    return rows


def build_dataframe(rows: list[dict[str, Any]]) -> pl.DataFrame:
    return pl.DataFrame(rows, schema_overrides=SCHEMA).sort("provider_id")


def load_provider_ids() -> list[str]:
    query = """
        with providers as (
            select distinct provider_id
            from model.storage_provider_sector_lifecycle_daily
            union
            select distinct provider_id
            from model.storage_provider_power_daily
            union
            select distinct provider_id
            from model.storage_provider_block_rewards_daily
            union
            select distinct provider_id
            from model.verified_claims
        )
        select provider_id
        from providers
        order by provider_id
    """
    with fdp.db_connection(read_only=True) as conn:
        return [provider_id for (provider_id,) in conn.execute(query).fetchall()]


async def load_tipset_key(client: httpx.AsyncClient) -> list[dict[str, str]]:
    response = await post_rpc(
        client,
        {"jsonrpc": "2.0", "id": 1, "method": "Filecoin.ChainHead", "params": []},
    )
    result = expect_dict(response.get("result"), "Filecoin.ChainHead result")
    cids = result.get("Cids")
    if not isinstance(cids, list) or not cids:
        raise ValueError("Filecoin.ChainHead returned an empty tipset key")
    return cids


async def fetch_chunk_rows(
    client: httpx.AsyncClient,
    provider_ids: list[str],
    tipset_key: list[dict[str, str]],
    fetched_at: dt.datetime,
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
    responses = await post_rpc(client, payload)

    results_by_provider = {provider_id: {} for provider_id in provider_ids}
    for response in responses:
        response_id = response.get("id")
        if not isinstance(response_id, str) or ":" not in response_id:
            raise ValueError(f"Unexpected JSON-RPC response id: {response_id!r}")

        provider_id, alias = response_id.split(":", 1)
        if provider_id not in results_by_provider:
            raise ValueError(f"Unexpected provider in JSON-RPC response: {provider_id}")

        error = response.get("error")
        if error is not None:
            error_json = json.dumps(error, sort_keys=True)
            raise ValueError(f"JSON-RPC error for {provider_id} {alias}: {error_json}")
        results_by_provider[provider_id][alias] = response.get("result")

    rows: list[dict[str, Any]] = []
    for provider_id in provider_ids:
        provider_results = results_by_provider[provider_id]
        missing_aliases = sorted(RPC_METHODS.keys() - provider_results.keys())
        if missing_aliases:
            missing = ", ".join(missing_aliases)
            raise ValueError(f"Missing JSON-RPC responses for {provider_id}: {missing}")
        rows.append(build_row(provider_id, provider_results, fetched_at))
    return rows


def build_row(
    provider_id: str,
    results: dict[str, Any],
    fetched_at: dt.datetime,
) -> dict[str, Any]:
    info = expect_dict(results["info"], f"StateMinerInfo result for {provider_id}")
    sector_count = expect_dict(
        results["sector_count"],
        f"StateMinerSectorCount result for {provider_id}",
    )
    market_balance = expect_dict(
        results["market_balance"],
        f"StateMarketBalance result for {provider_id}",
    )
    state_result = expect_dict(
        results["state"], f"StateReadState result for {provider_id}"
    )
    state = expect_dict(
        state_result.get("State"), f"StateReadState.State for {provider_id}"
    )

    market_escrow_fil = atto_fil_to_fil(market_balance.get("Escrow"))
    market_locked_fil = atto_fil_to_fil(market_balance.get("Locked"))
    market_available_fil = (
        market_escrow_fil - market_locked_fil
        if market_escrow_fil is not None and market_locked_fil is not None
        else None
    )

    return {
        "provider_id": provider_id,
        "owner_id": null_if_empty(info.get("Owner")),
        "worker_id": null_if_empty(info.get("Worker")),
        "beneficiary_id": null_if_empty(info.get("Beneficiary")),
        "peer_id": null_if_empty(info.get("PeerId")),
        "control_addresses": json_array_string(info.get("ControlAddresses")),
        "multi_addresses": json_array_string(
            decoded_multiaddrs(info.get("Multiaddrs"))
        ),
        "sector_size": info.get("SectorSize"),
        "live_sectors": sector_count.get("Live"),
        "active_sectors": sector_count.get("Active"),
        "faulty_sectors": sector_count.get("Faulty"),
        "actor_balance_fil": atto_fil_to_fil(state_result.get("Balance")),
        "available_balance_fil": atto_fil_to_fil(results["available_balance"]),
        "market_escrow_fil": market_escrow_fil,
        "market_locked_fil": market_locked_fil,
        "market_available_fil": market_available_fil,
        "initial_pledge_fil": atto_fil_to_fil(state.get("InitialPledge")),
        "locked_funds_fil": atto_fil_to_fil(state.get("LockedFunds")),
        "pre_commit_deposits_fil": atto_fil_to_fil(state.get("PreCommitDeposits")),
        "fee_debt_fil": atto_fil_to_fil(state.get("FeeDebt")),
        "fetched_at": fetched_at,
    }


async def post_rpc(
    client: httpx.AsyncClient, payload: dict[str, Any] | list[dict[str, Any]]
) -> Any:
    response = await client.post(RPC_URL, json=payload)
    response.raise_for_status()
    return response.json()


def expect_dict(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"Expected object for {context}, got {type(value).__name__}")
    return value


def atto_fil_to_fil(value: Any) -> float | None:
    normalized = null_if_empty(value)
    if normalized is None:
        return None
    return float(Decimal(normalized) / ATTO_FIL)


def decoded_multiaddrs(value: Any) -> list[str]:
    return [
        str(Multiaddr(base64.b64decode(encoded)))
        for encoded in non_empty_strings(value)
    ]


def json_array_string(value: Any) -> str | None:
    values = non_empty_strings(value)
    return json.dumps(values) if values else None


def non_empty_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [
        normalized for item in value if (normalized := null_if_empty(item)) is not None
    ]


def null_if_empty(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return None if not normalized or normalized == "<empty>" else normalized


def chunked[T](values: list[T], size: int) -> list[list[T]]:
    return [values[index : index + size] for index in range(0, len(values), size)]
