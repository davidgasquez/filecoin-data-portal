# asset.description = Runtime registry of FEVM mainnet contracts and their ABI
# JSONs from GitHub or Blockscout.

# asset.column = chain_id | Filecoin EVM chain id.
# asset.column = network | Human-readable network name.
# asset.column = contract_name | Logical decoder name used downstream.
# asset.column = abi_name | Human-readable ABI identifier.
# asset.column = deployment_key | Upstream deployment key or null for manual
# entries.
# asset.column = deployment_role | Address role: proxy, implementation, view,
# or address.
# asset.column = address | Contract address that emitted logs, normalized to
# lowercase.
# asset.column = implementation_address | Implementation address when the ABI
# was resolved through a proxy.
# asset.column = source_kind | ABI/address resolution strategy.
# asset.column = source_name | Upstream host or repository label.
# asset.column = address_source_url | Upstream URL used to resolve the address, if any.
# asset.column = abi_source_url | Upstream URL used to fetch the ABI, if any.
# asset.column = abi_json | Raw ABI JSON normalized to a sorted JSON string.
# asset.column = source_version | Upstream version or commit, if any.
# asset.column = fetched_at | Timestamp when this registry snapshot was fetched.

import datetime as dt
import json
from dataclasses import dataclass
from typing import cast

import httpx
import polars as pl

MAINNET_CHAIN_ID = 314
MAINNET_NETWORK = "mainnet"
BLOCKSCOUT_BASE_URL = "https://filecoin.blockscout.com"
GITHUB_SOURCE_REPO = "FilOzone/filecoin-services"
GITHUB_SOURCE_REF = "main"
GITHUB_RAW_BASE = (
    f"https://raw.githubusercontent.com/{GITHUB_SOURCE_REPO}/{GITHUB_SOURCE_REF}"
    "/service_contracts"
)
GITHUB_DEPLOYMENTS_URL = f"{GITHUB_RAW_BASE}/deployments.json"


@dataclass(frozen=True, slots=True)
class GitHubDeploymentContract:
    contract_name: str
    abi_name: str
    deployment_key_prefix: str


@dataclass(frozen=True, slots=True)
class BlockscoutProxyContract:
    contract_name: str
    abi_name: str
    proxy_address: str


GITHUB_CONTRACTS = [
    GitHubDeploymentContract("filecoin_pay_v1", "FilecoinPayV1", "FILECOIN_PAY"),
    GitHubDeploymentContract(
        "filecoin_warm_storage_service",
        "FilecoinWarmStorageService",
        "FWSS",
    ),
    GitHubDeploymentContract(
        "filecoin_warm_storage_service_state_view",
        "FilecoinWarmStorageServiceStateView",
        "FWSS_VIEW",
    ),
    GitHubDeploymentContract("pdp_verifier", "PDPVerifier", "PDP_VERIFIER"),
    GitHubDeploymentContract("provider_id_set", "ProviderIdSet", "ENDORSEMENT_SET"),
    GitHubDeploymentContract(
        "service_provider_registry",
        "ServiceProviderRegistry",
        "SERVICE_PROVIDER_REGISTRY",
    ),
    GitHubDeploymentContract(
        "session_key_registry",
        "SessionKeyRegistry",
        "SESSION_KEY_REGISTRY",
    ),
]

BLOCKSCOUT_PROXY_CONTRACTS = [
    BlockscoutProxyContract(
        "usdfc_debt_token",
        "DebtToken",
        "0x80B98d3aa09ffff255c3ba4A241111Ff1262F045",
    ),
    BlockscoutProxyContract(
        "usdfc_stability_pool",
        "StabilityPool",
        "0x791Ad78bBc58324089D3E0A8689E7D045B9592b5",
    ),
    BlockscoutProxyContract(
        "usdfc_trove_manager",
        "TroveManager",
        "0x5aB87c2398454125Dd424425e39c8909bBE16022",
    ),
    BlockscoutProxyContract(
        "usdfc_active_pool",
        "ActivePool",
        "0x8637Ac7FdBB4c763B72e26504aFb659df71c7803",
    ),
    BlockscoutProxyContract(
        "usdfc_default_pool",
        "DefaultPool",
        "0xAda716f497da8EC9F766F9a94779E1b6e73d29fF",
    ),
]


def normalize_address(address: str) -> str:
    normalized = address.strip().lower()
    if not normalized.startswith("0x") or len(normalized) != 42:
        raise ValueError(f"Invalid address: {address}")
    return normalized


def normalize_abi_json(abi: object) -> str:
    if not isinstance(abi, list):
        raise TypeError(f"ABI must be a JSON list, got {type(abi).__name__}")
    return json.dumps(abi, sort_keys=True)


def fetch_json(client: httpx.Client, url: str) -> object:
    return client.get(url).raise_for_status().json()


def fetch_blockscout_abi(client: httpx.Client, address: str) -> str:
    payload = cast(
        dict[str, object],
        fetch_json(
            client,
            f"{BLOCKSCOUT_BASE_URL}/api?module=contract&action=getabi&address={address}",
        ),
    )
    if "result" not in payload:
        raise TypeError(f"Unexpected Blockscout ABI payload for {address}")

    result = payload["result"]
    abi = json.loads(result) if isinstance(result, str) else result
    return normalize_abi_json(abi)


def fetch_blockscout_implementation(client: httpx.Client, proxy_address: str) -> str:
    payload = cast(
        dict[str, object],
        fetch_json(
            client,
            f"{BLOCKSCOUT_BASE_URL}/api/v2/smart-contracts/{proxy_address}",
        ),
    )
    implementations = cast(list[object], payload.get("implementations") or [])
    if len(implementations) != 1:
        raise ValueError(
            "Expected exactly one implementation for "
            f"{proxy_address}, got {len(implementations)}"
        )

    implementation = cast(dict[str, object], implementations[0])
    if "address_hash" not in implementation:
        raise TypeError(f"Unexpected implementation payload for {proxy_address}")
    return normalize_address(str(implementation["address_hash"]))


def resolve_github_rows(client: httpx.Client, fetched_at: dt.datetime) -> list[dict]:
    deployments = cast(dict[str, object], fetch_json(client, GITHUB_DEPLOYMENTS_URL))
    chain = cast(dict[str, object], deployments[str(MAINNET_CHAIN_ID)])
    metadata = cast(dict[str, object], chain.get("metadata") or {})
    source_version = str(metadata.get("commit") or "")

    rows: list[dict] = []
    for spec in GITHUB_CONTRACTS:
        abi_url = f"{GITHUB_RAW_BASE}/abi/{spec.abi_name}.abi.json"
        abi_json = normalize_abi_json(fetch_json(client, abi_url))
        matching_keys = sorted(
            key
            for key in chain
            if key.startswith(f"{spec.deployment_key_prefix}_")
            and key.endswith("_ADDRESS")
        )
        if not matching_keys:
            raise ValueError(
                "No deployment keys found for "
                f"{spec.contract_name} ({spec.deployment_key_prefix})"
            )

        for key in matching_keys:
            role = (
                "proxy"
                if key.endswith("_PROXY_ADDRESS")
                else "implementation"
                if key.endswith("_IMPLEMENTATION_ADDRESS")
                else "view"
                if key.endswith("_VIEW_ADDRESS")
                else "address"
            )
            rows.append({
                "chain_id": MAINNET_CHAIN_ID,
                "network": MAINNET_NETWORK,
                "contract_name": spec.contract_name,
                "abi_name": spec.abi_name,
                "deployment_key": key,
                "deployment_role": role,
                "address": normalize_address(str(chain[key])),
                "implementation_address": None,
                "source_kind": "github_deployments",
                "source_name": GITHUB_SOURCE_REPO,
                "address_source_url": GITHUB_DEPLOYMENTS_URL,
                "abi_source_url": abi_url,
                "abi_json": abi_json,
                "source_version": source_version,
                "fetched_at": fetched_at,
            })
    return rows


def resolve_blockscout_proxy_rows(
    client: httpx.Client,
    fetched_at: dt.datetime,
) -> list[dict]:
    rows: list[dict] = []
    for spec in BLOCKSCOUT_PROXY_CONTRACTS:
        proxy_address = normalize_address(spec.proxy_address)
        address_source_url = (
            f"{BLOCKSCOUT_BASE_URL}/api/v2/smart-contracts/{proxy_address}"
        )
        implementation_address = fetch_blockscout_implementation(client, proxy_address)
        abi_source_url = (
            f"{BLOCKSCOUT_BASE_URL}/api"
            f"?module=contract&action=getabi&address={implementation_address}"
        )
        rows.append({
            "chain_id": MAINNET_CHAIN_ID,
            "network": MAINNET_NETWORK,
            "contract_name": spec.contract_name,
            "abi_name": spec.abi_name,
            "deployment_key": None,
            "deployment_role": "proxy",
            "address": proxy_address,
            "implementation_address": implementation_address,
            "source_kind": "blockscout_proxy_impl",
            "source_name": "filecoin.blockscout.com",
            "address_source_url": address_source_url,
            "abi_source_url": abi_source_url,
            "abi_json": fetch_blockscout_abi(client, implementation_address),
            "source_version": None,
            "fetched_at": fetched_at,
        })
    return rows


def contract_registry() -> pl.DataFrame:
    fetched_at = dt.datetime.now(dt.UTC).replace(tzinfo=None)

    with httpx.Client(follow_redirects=True, timeout=30) as client:
        rows = [
            *resolve_github_rows(client, fetched_at),
            *resolve_blockscout_proxy_rows(client, fetched_at),
        ]

    return pl.DataFrame(
        rows, schema_overrides={"chain_id": pl.Int64, "fetched_at": pl.Datetime}
    ).sort("contract_name", "deployment_role", "address")
