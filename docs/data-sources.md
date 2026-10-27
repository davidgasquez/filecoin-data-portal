# Filecoin data sources

Updated 2026-10-27.

Start with the Filecoin API or MCP for Onchain Cloud data, Lily for chain history, and JSON-RPC for direct state reads.

| Source | Useful for | Access |
| --- | --- | --- |
| [Filecoin API](https://api.filecoin.io/docs) | Onchain Cloud providers, data sets, pieces, payment rails, settlements, and session keys. | Public read-only REST; [OpenAPI](https://api.filecoin.io/openapi.json). Prefix queries with `/mainnet` or `/calibration`. |
| [Filecoin MCP](https://mcp.filecoin.io/server-card) | The same Onchain Cloud data for agents, plus Filecoin documentation search. | Streamable HTTP at `https://mcp.filecoin.io`; no API key. [Implementation](https://github.com/filecoin-project/agents/tree/main/apps/filecoin-api). |
| [Hyperion](https://github.com/fidlabs/hyperion) | PoRep Market deals, onboarded data, deal values, payment histories, and provider IPNI reporting. | REST implementation with Swagger at `/docs`. Public instance URL unconfirmed; README is marked WIP. |
| [Filecoin Pay Volume indexer](https://fpv-indexer.allocator.tech/) | Service orchestrators, payments, and quarterly volumes calculated under FIP-0118. | Public read-only REST with OpenAPI at the root; [source and calibration instance](https://github.com/fidlabs/fpv-indexer). |
| [Lily / Sentinel](https://lilium.sh/data/dumps) | Historical actors, messages, receipts, power, sectors, rewards, gas, and market deals. | BigQuery SQL over `lily-data.lily`; needs a Google Cloud billing project and query permissions. Table freshness varies. |
| [RIBA chain archive](https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/raw/fevm/eth_logs.py) | Bulk FEVM receipts and event logs for rebuilding contract histories. | Daily Brotli-compressed NDJSON at `chain.data.riba.plus`; URL pattern in the linked loader. Partitions may be missing. |
| [Filecoin Data Portal](https://filecoindataportal.xyz/datasets) | Ready-to-query daily metrics and entity tables across network, providers, storage, and payments. | Public Parquet downloads; [usage and upstream sources](https://filecoindataportal.xyz/docs). |
| [PDP Explorer](https://pdp.filecoin.cloud/mainnet) and [Pay Explorer](https://pay.filecoin.cloud/mainnet) | PDP proofs and faults; payment rails, settlements, accounts, and operators. | Dashboards backed by GraphQL subgraphs: [PDP](https://github.com/FilOzone/pdp-explorer/blob/main/docs/subgraph/graphql-api.md), [Pay](https://github.com/FilOzone/filecoin-pay-explorer). |
| [ProbeLab FOC](https://probelab.io/filecoin/foc/) / [Dealbot](https://dealbot.filoz.org/) | Onchain Cloud provider storage, retrieval, proving, pull, and sampled-retrieval checks. Results are probe observations, not all client traffic. | Dashboard, daily [Parquet backups and CSV index](https://probelab.io/filecoin/foc/backups/), [methodology](https://probelab.io/filecoin/foc/methodology/), and [source documentation](https://github.com/FilOzone/dealbot/tree/main/docs/checks). |
| [ProbeLab network monitoring](https://probelab.io/filecoin/) | Peer counts, client versions, network geography, and cloud-provider distribution. | [Topology dashboard and measurement notes](https://probelab.io/filecoin/topology/). |
| [Beryx](https://docs.zondax.ch/beryx-api) | Indexed account transactions, multisig interactions, and fees. | REST API and explorer; API token required. |
| [IPNI / CID Contact](https://cid.contact/) | Finding providers and advertised retrieval methods for a CID. | Public content-routing queries; [documentation](https://docs.cid.contact/). Advertisements show discoverability, not retrievability. |

For individual transactions, actors, and contracts, use [Filfox](https://filfox.info/) and [Blockscout](https://filecoin.blockscout.com/).

## JSON-RPC endpoints

These mainnet endpoints returned chain ID `314` in read-only checks on 2026-10-27:

| Provider | Endpoint |
| --- | --- |
| [GLIF](https://api.node.glif.io/) | `https://api.node.glif.io/rpc/v1` |
| [Chain.Love](https://filecoin.chain.love/) | `https://api.chain.love/rpc/v1` |

Use `Filecoin.*` methods for native chain state and `eth_*` methods for FEVM reads. The [official RPC directory](https://docs.filecoin.io/networks-and-tools/networks/mainnet/rpcs) lists more providers. Most public endpoints guarantee only recent state (about 2,000 blocks); for older state, use an archive node or an indexed source such as Lily. The chain-ID check does not verify archive depth or throughput.
