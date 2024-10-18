---
title: "Data Sources"
format:
  html:
    toc: false
---

Most of the data used through the portal comes from the Filecoin chain. There is also some off-chain data like [Datacap Applications](https://docs.filecoin.io/basics/how-storage-works/filecoin-plus) or [Storage Provider's Reputation scores](https://filecoin.io/blog/posts/reputation-systems-in-filecoin/) that are collected from other places.

## Deals

Deals data is available on chain and can be obtained in different ways:

- Doing a `StateMarketDeals` JSON-RPC call and parsing the returned JSON. If you don't have a node running, you can use [Glif nodes](https://lotus.filecoin.io/lotus/developers/glif-nodes/) `StateMarketDeals` periodic dump on S3 ([direct link](https://marketdeals.s3.amazonaws.com/StateMarketDeals.json.zst)).
- Using an [oracle like `fil-naive-marketwatch`](https://github.com/ribasushi/fil-naive-marketwatch).
- Reconstructing the deals state [from Lily](https://lilium.sh/) tables.

## Clients

Clients can be derived from the [deals](#deals) dataset and expanded with the following sources:

- Datacap. From [Datacap Stats API](https://datacapstats.io/) calling `https://api.datacapstats.io/api/getVerifiedClients`. You get a JSON of verified clients in the FIL+ program that contains client names, Datacap application data and other self-reported data. Alternatively, this data can be obtained by parsing the relevant GitHub repositories issues and comments.

## Storage Providers

Storage Providers be derived from the [deals](#deals) dataset. More information about proviers can be collected in the following sources:

- Location using the different [provider.quest](https://provider.quest/) endpoints/datasets.

### Retrieval Data

Retrieval data is available from the [Spark API](https://spark-api.super.site/).

### Reputation Data

Reputation is both obtained from [FilRep](https://filrep.io/) ([methodology](https://filrep.io/methodology)) and augmented with custom metrics around deals. For example, what is the average replication of a deal for the SP?

### Energy Data

Energy data is available from [Filecoin Green](https://filecoin.energy/) ([Model API](https://api.filecoin.energy/docs) and [Green Scores API](https://sp-outputs-api.vercel.app/api-docs/))

## FVM

Filecoin Virtual Machine data is trickier to get. Some sources:

- Directly from the [FVM](https://fvm.starboard.ventures/) dashboard.
- Some metrics are available in the [Spacescope API](https://docs.spacescope.io/version_history#v240-on-march-16-2023)

## Messages

A few teams across the ecosystem are indexing Filecoin Messages. The most comprehensive source are [Beryx](https://beryx.zondax.ch/) and [FilInfo](https://filinfo.io/docs).

## Data Indexers

Besides the data sources mentioned above, there are a few data indexers that provide data in a more structured way.

- [Starboard](https://dashboard.starboard.ventures/dashboard) - [FVM](https://fvm.starboard.ventures/)
- [Dev Storage](https://dev.storage/)
- [Beryx](https://beryx.zondax.ch/)
- [Spacegap](https://spacegap.github.io)
- [Filecoin Green](https://filecoin.energy/)
- [Filecoin CID Checker](https://filecoin.tools/)
- [File.app](https://file.app/)
- [Gliff Explorer](https://explorer.glif.io/)
- [DMOB Messages Database](https://digitalmob.ro/) powering [FilInfo](https://filinfo.io/docs)
- [Filrep](https://filrep.io/)
- [FilecoinGreen](https://filecoin.energy/)
- [FilFox](https://filfox.info) and [API](https://filfox.info/api)
- [FilScan](https://filscan.io) and [API](https://api-v2.filscan.io/api)
- [Filutils](https://filutils.com/) decoding message params ([example](https://www.filutils.com/en/message/bafy2bzacec42jewhmgx73yxd7bndj6p7z5n3xibx47vex2woch66wbip434oa)).
- [Blockscout](https://filecoin.blockscout.com/) and [API](https://filecoin.blockscout.com/api-docs) for FEVM.

### JSON-RPC Endpoints

Nodes usually implement all the [JSON-RPC methods](https://docs.filecoin.io/reference/json-rpc) needed to get the data.

- Glif - `https://api.node.glif.io`
- Zondax - `https://api.zondax.ch/fil/node/mainnet/rpc/v1`
- Laconic - `https://fil-mainnet-1.rpc.laconic.com/rpc/v1`
- Provider Quest - `https://lotus.miner.report/mainnet_api/0/node/rpc/v0`
- More at [filecoin.io docs](https://docs.filecoin.io/networks/mainnet/rpcs)!
- More at [Chainlist](https://chainlist.org/chain/314)!

### Code

- [BlockScience](https://github.com/BlockScience)
- [Filecoin Mecha Twin](https://github.com/protocol/filecoin-mecha-twin)
- [PyLotus](https://github.com/FilForge/pylotus-rpc/)
