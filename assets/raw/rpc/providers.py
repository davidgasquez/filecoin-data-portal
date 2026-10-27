# asset.description = PDP provider registry snapshots and endorsements.

# asset.depends = raw.contracts_registry
# asset.depends = raw.riba_eth_logs_decoded

# asset.materialization = dataframe
# asset.keep_existing_on_failure = true

# asset.column = provider_id | Service provider registry identifier.
# asset.column = provider_address | Provider control address.
# asset.column = payee | Payee address.
# asset.column = name | Provider name declared in the registry.
# asset.column = description | Provider description declared in the registry.
# asset.column = is_active | Whether the registry marks the provider active.
# asset.column = is_endorsed | Whether the provider is in the endorsement set.
# asset.column = block_number | Chain block used for the snapshot.
# asset.column = fetched_at | Snapshot fetch timestamp.

# asset.not_null = provider_id
# asset.not_null = provider_address
# asset.not_null = is_active
# asset.not_null = is_endorsed
# asset.not_null = block_number
# asset.not_null = fetched_at
# asset.unique = provider_id
# asset.assert = provider_id > 0
# asset.assert = provider_address != '0x' || repeat('0', 40)

import datetime as dt
import os

import polars as pl
from requests import RequestException
from web3 import Web3
from web3.exceptions import Web3Exception
from web3.providers.rpc.utils import ExceptionRetryConfiguration

import fdp

DEFAULT_RPC_URLS = (
    "https://api.node.glif.io/rpc/v1",
    "https://api.chain.love/rpc/v1",
    "https://filecoin.chainup.net/rpc/v1",
)
SCHEMA = {
    "provider_id": pl.Int64,
    "provider_address": pl.String,
    "payee": pl.String,
    "name": pl.String,
    "description": pl.String,
    "is_active": pl.Boolean,
    "is_endorsed": pl.Boolean,
    "block_number": pl.Int64,
    "fetched_at": pl.Datetime,
}


def providers() -> pl.DataFrame:
    with fdp.db_connection(read_only=True) as conn:
        contracts = {
            name: (address, abi)
            for name, address, abi in conn.execute("""
                select contract_name, address, abi_json
                from raw.contracts_registry
                where (contract_name = 'service_provider_registry'
                       and deployment_role = 'proxy')
                   or (contract_name = 'provider_id_set'
                       and deployment_role = 'address')
            """).fetchall()
        }
        provider_ids = [
            row[0]
            for row in conn.execute("""
                select distinct
                    cast(json_extract_string(args, '$.providerId') as bigint)
                from raw.riba_eth_logs_decoded
                where contract_name = 'service_provider_registry'
                  and event_name = 'ProviderRegistered'
                order by 1
            """).fetchall()
        ]
        block_row = conn.execute(
            "select max(block_number) from raw.riba_eth_logs_decoded"
        ).fetchone()

    if not provider_ids:
        return pl.DataFrame(schema=SCHEMA)
    if block_row is None or block_row[0] is None:
        raise ValueError("No indexed chain block for the PDP registry snapshot")
    block_number = int(block_row[0])

    rpc_urls = (
        tuple(
            url.strip()
            for url in os.getenv(
                "FDP_FILECOIN_RPC_URLS", ",".join(DEFAULT_RPC_URLS)
            ).split(",")
            if url.strip()
        )
        or DEFAULT_RPC_URLS
    )
    last_error: Exception | None = None
    for url in rpc_urls:
        try:
            web3 = Web3(
                Web3.HTTPProvider(
                    url,
                    request_kwargs={"timeout": 30},
                    exception_retry_configuration=ExceptionRetryConfiguration(
                        errors=(RequestException,), retries=2
                    ),
                )
            )
            registry_address, registry_abi = contracts["service_provider_registry"]
            registry = web3.eth.contract(
                address=Web3.to_checksum_address(registry_address), abi=registry_abi
            )
            set_address, set_abi = contracts["provider_id_set"]
            endorsement_set = web3.eth.contract(
                address=Web3.to_checksum_address(set_address), abi=set_abi
            )
            endorsed_ids = set(
                endorsement_set.functions.getProviderIds().call(
                    block_identifier=block_number
                )
            )
            fetched_at = dt.datetime.now(dt.UTC).replace(tzinfo=None)
            rows = []
            for provider_id in provider_ids:
                # The bulk getter omits removed providers; this getter retains them.
                address, payee, name, description, active = (
                    registry.functions.providers(provider_id).call(
                        block_identifier=block_number
                    )
                )
                rows.append({
                    "provider_id": provider_id,
                    "provider_address": address.lower(),
                    "payee": payee.lower(),
                    "name": name,
                    "description": description,
                    "is_active": active,
                    "is_endorsed": provider_id in endorsed_ids,
                    "block_number": block_number,
                    "fetched_at": fetched_at,
                })
            return pl.DataFrame(rows, schema=SCHEMA)
        except (RequestException, Web3Exception) as error:
            last_error = error

    raise RuntimeError(
        "PDP registry snapshot failed across all RPC endpoints"
    ) from last_error
