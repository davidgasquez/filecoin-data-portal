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
from itertools import batched
from typing import Any

import httpx
import polars as pl
from multiaddr import Multiaddr

import fdp

RPC_URL = "https://filecoin.chain.love/rpc"
BATCH_SIZE = 100
MAX_CONCURRENT = 24
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
    rows = asyncio.run(load_rows())
    return pl.DataFrame(rows, schema_overrides=SCHEMA).sort("provider_id")


async def load_rows() -> list[dict[str, Any]]:
    fetched_at = dt.datetime.now(dt.UTC).replace(tzinfo=None)
    provider_ids = load_provider_ids()
    limits = httpx.Limits(
        max_connections=MAX_CONCURRENT, max_keepalive_connections=MAX_CONCURRENT
    )
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async with httpx.AsyncClient(
        follow_redirects=True, timeout=120, limits=limits
    ) as client:
        tipset_key = await fetch_tipset_key(client)

        async def fetch(chunk: tuple[str, ...]) -> list[dict[str, Any]]:
            async with semaphore:
                return await fetch_chunk(client, chunk, tipset_key, fetched_at)

        chunks = list(batched(provider_ids, BATCH_SIZE, strict=False))
        results = await asyncio.gather(*(fetch(chunk) for chunk in chunks))
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

    results: dict[str, dict[str, Any]] = {pid: {} for pid in provider_ids}
    for response in responses:
        provider_id, alias = response["id"].split(":", 1)
        if response.get("error"):
            raise ValueError(
                f"JSON-RPC error for {provider_id} {alias}: {response['error']}"
            )
        results[provider_id][alias] = response["result"]

    return [build_row(pid, results[pid], fetched_at) for pid in provider_ids]


def build_row(
    provider_id: str, results: dict[str, Any], fetched_at: dt.datetime
) -> dict[str, Any]:
    info = results["info"]
    sector_count = results["sector_count"]
    market = results["market_balance"]
    state_result = results["state"]
    state = state_result["State"]

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
        "available_balance_fil": atto_to_fil(results["available_balance"]),
        "market_escrow_fil": escrow,
        "market_locked_fil": locked,
        "market_available_fil": available,
        "initial_pledge_fil": atto_to_fil(state.get("InitialPledge")),
        "locked_funds_fil": atto_to_fil(state.get("LockedFunds")),
        "pre_commit_deposits_fil": atto_to_fil(state.get("PreCommitDeposits")),
        "fee_debt_fil": atto_to_fil(state.get("FeeDebt")),
        "fetched_at": fetched_at,
    }


async def post_rpc(client: httpx.AsyncClient, payload: Any) -> Any:
    response = await client.post(RPC_URL, json=payload)
    response.raise_for_status()
    return response.json()


def atto_to_fil(value: Any) -> float | None:
    cleaned = null_if_empty(value)
    return float(Decimal(cleaned) / ATTO_FIL) if cleaned else None


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
