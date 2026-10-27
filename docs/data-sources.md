# Filecoin data sources

Updated 2026-10-27.

Start with the Filecoin API or MCP for Onchain Cloud data, Lily for chain history, and JSON-RPC for direct state reads.

| Source | Useful for | Access |
| --- | --- | --- |
| [Filecoin API](https://api.filecoin.io/docs) | Onchain Cloud providers, data sets, pieces, payment rails, settlements, and session keys. | Public read-only REST; [OpenAPI](https://api.filecoin.io/openapi.json). Prefix queries with `/mainnet` or `/calibration`. |
| [Filecoin MCP](https://mcp.filecoin.io/server-card) | The same Onchain Cloud data for agents, plus Filecoin documentation search. | Streamable HTTP at `https://mcp.filecoin.io`; no API key. [Implementation](https://github.com/filecoin-project/agents/tree/main/apps/filecoin-api). |
| [Hyperion](https://github.com/fidlabs/hyperion) | PoRep Market deals, onboarded data, deal values, payment histories, and provider IPNI reporting. | REST implementation with Swagger at `/docs`. Public instance URL unconfirmed; README is marked WIP. |
| [Solstice contracts](https://github.com/filecoin-project/solstice/tree/b9a63a87b5adee272c16d7e507cc9c127fb34f0f) | Service Orchestrator admissions, bindings, volume declarations and gate outcomes. | Pinned deployments and Blockscout-verified ABIs; events from RIBA. |
| [Filecoin Pay Volume indexer](https://fpv-indexer.allocator.tech/) | Reference comparison for Service Orchestrator payments and quarterly FPV. | Public read-only REST with OpenAPI at the root; [source and calibration instance](https://github.com/fidlabs/fpv-indexer). Not a production input. |
| [Lily / Sentinel](https://lilium.sh/data/dumps) | Historical actors, messages, receipts, power, sectors, rewards, gas, and market deals. | BigQuery SQL over `lily-data.lily`; needs a Google Cloud billing project and query permissions. Table freshness varies. |
| [RIBA chain archive](https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/raw/riba/eth_logs.py) | Bulk FEVM receipts and event logs for rebuilding contract histories. | Daily Brotli-compressed NDJSON at `chain.data.riba.plus`; URL pattern in the linked loader. Partitions may be missing. |
| [Blockscout](https://filecoin.blockscout.com/) | Fee-auction call traces, including nested calls, for FIL FPV valuation. | Public REST: `/api/v2/transactions/{hash}/raw-trace`; candidate discovery through advanced filters and RIBA logs. |
| [DefiLlama](https://api-docs.defillama.com/) | Filecoin DeFi TVL, per-protocol TVL, USDFC supply, and GLIF iFIL yield history. | Public REST, no key: `api.llama.fi`, `stablecoins.llama.fi`, `yields.llama.fi`. Series are dated by DefiLlama snapshot time, not end of day. Chain TVL excludes liquid staking; GLIF TVL is sourced from GLIF's indexer and includes borrower collateral. |
| [Filecoin Data Portal](https://filecoindataportal.xyz/datasets) | Ready-to-query daily metrics and entity tables across network, providers, storage, and payments. | Public Parquet downloads; [usage and upstream sources](https://filecoindataportal.xyz/docs). |
| [PDP Explorer](https://pdp.filecoin.cloud/mainnet) and [Pay Explorer](https://pay.filecoin.cloud/mainnet) | PDP proofs and faults; payment rails, settlements, accounts, and operators. | Dashboards backed by GraphQL subgraphs: [PDP](https://github.com/FilOzone/pdp-explorer/blob/main/docs/subgraph/graphql-api.md), [Pay](https://github.com/FilOzone/filecoin-pay-explorer). |
| [ProbeLab FOC](https://probelab.io/filecoin/foc/) / [Dealbot](https://dealbot.filoz.org/) | Onchain Cloud provider storage, retrieval, proving, pull, and sampled-retrieval checks. Results are probe observations, not all client traffic. | Dashboard, daily [Parquet backups and CSV index](https://probelab.io/filecoin/foc/backups/), [methodology](https://probelab.io/filecoin/foc/methodology/), and [source documentation](https://github.com/FilOzone/dealbot/tree/main/docs/checks). |
| [ProbeLab network monitoring](https://probelab.io/filecoin/) | Peer counts, client versions, network geography, and cloud-provider distribution. | [Topology dashboard and measurement notes](https://probelab.io/filecoin/topology/). |
| [Beryx](https://docs.zondax.ch/beryx-api) | Indexed account transactions, multisig interactions, and fees. | REST API and explorer; API token required. |
| [IPNI / CID Contact](https://cid.contact/) | Finding providers and advertised retrieval methods for a CID. | Public content-routing queries; [documentation](https://docs.cid.contact/). Advertisements show discoverability, not retrievability. |

For individual transactions, actors, and contracts, use [Filfox](https://filfox.info/) and [Blockscout](https://filecoin.blockscout.com/).

Provider quality uses ProbeLab for offchain checks and onchain PDP/FWSS events for proving. Proofs are dated when accepted; closed and faulted periods are dated when the contract closes them. The fault rate compares the same closed periods. A stalled data set's missed periods remain uncounted until its next proving-period call closes them; zero closures do not imply healthy proving. Missing archive partitions or stale decoded partitions make proving unavailable from that date until repaired. The old overdue estimate is omitted: reconstructing it correctly requires proving deadlines, deletions and payment termination.

Quarterly FPV uses admitted stablecoin payments and fee-auction traces for FIL valuation. FIL awaiting a qualifying print remains pending; missing inputs remain NULL. SRA posts, corrections and bound volumes are separate onchain facts. Gate columns describe observed checks, and Q1 is ungated; absent share-submission events do not prove that no submission occurred.

## JSON-RPC endpoints

These mainnet endpoints returned chain ID `314` in read-only checks on 2026-10-27:

| Provider | Endpoint |
| --- | --- |
| [GLIF](https://api.node.glif.io/) | `https://api.node.glif.io/rpc/v1` |
| [Chain.Love](https://filecoin.chain.love/) | `https://api.chain.love/rpc/v1` |

Use `Filecoin.*` methods for native chain state and `eth_*` methods for FEVM reads. The [official RPC directory](https://docs.filecoin.io/networks-and-tools/networks/mainnet/rpcs) lists more providers. Most public endpoints guarantee only recent state (about 2,000 blocks); for older state, use an archive node or an indexed source such as Lily. The chain-ID check does not verify archive depth or throughput.
