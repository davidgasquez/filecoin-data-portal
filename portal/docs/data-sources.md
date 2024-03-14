# Data Sources

Most of the data used through the portal comes from the Filecoin chain itself. There is also some off-chain data like [Datacap Applications](https://docs.filecoin.io/basics/how-storage-works/filecoin-plus) or [Storage Provider's Reputation scores](https://filecoin.io/blog/posts/reputation-systems-in-filecoin/) that are collected from other places.

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

## FVM

Filecoin Virtual Machine data is trickier to get. Some sources:

- Directly from the [FVM](https://fvm.starboard.ventures/) dashboard.
- Some metrics are available in the [Spacescope API](https://docs.spacescope.io/version_history#v240-on-march-16-2023)

## Messages

A few teams across the ecosystem are indexing Filecoin Messages. The most comprehensive source are [Beriz](https://beryx.zondax.ch/) and [FilInfo](https://filinfo.io/docs).

# Data Sources

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

## Notebooks

- [BlockScience](https://github.com/BlockScience)
- [Filecoin Mecha Twin](https://github.com/protocol/filecoin-mecha-twin)
