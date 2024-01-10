# Filecoin Anlytitcs Data Sources

Most of the data used is coming from the Filecoin chain itself. However, there is some off-chain data like [Datacap Applications](https://docs.filecoin.io/basics/how-storage-works/filecoin-plus) or [Storage Provider's Reputation scores](https://filecoin.io/blog/posts/reputation-systems-in-filecoin/) that we pull from other public places. Each data "entity" comes from the best source available and is augmented with data from other sources.

## Deals

Deals data is available on chain and can be obtained via different ways.

- Doing a `StateMarketDeals` JSON-RPC call and parsing the returned JSON. If you don't have a node running, you can use [Glif nodes](https://lotus.filecoin.io/lotus/developers/glif-nodes/) `StateMarketDeals` periodic dump on S3 ([direct link](https://marketdeals.s3.amazonaws.com/StateMarketDeals.json.zst)).
- Using an [oracle like `fil-naive-marketwatch`](https://github.com/ribasushi/fil-naive-marketwatch).
- Reconstructing the deals state [from Lily](https://lilium.sh/) tables.

This data only shows current state so deals that aren't part of it anymore are not taken into account.

## Clients

Can be derived from the [deals](#deals) table. Clients can be augmented with the following sources:

- Datacap. From [Datacap Stats API](https://datacapstats.io/) calling `https://api.datacapstats.io/api/getVerifiedClients`. You get a JSON of verified clients in the FIL+ program that contains client names, Datacap application data and other self-reported data. Alternatively, this data can be obtained by parsing the relevant GitHub repositories issues and comments.

## Storage Providers

Can be derived from the [deals](#deals) table. Storage Providers cab ve augmented with the following sources:

- Location using the different [provider.quest](https://provider.quest/) endpoints/datasets.

## Indexers

- [Starboard](https://dashboard.starboard.ventures/dashboard) - [FVM](https://fvm.starboard.ventures/)
- [Dev Storage](https://dev.storage/)
- [Beryz](https://beryx.zondax.ch/)
- [Spacegap](https://spacegap.github.io)
- [Filecoin Green](https://filecoin.energy/)
- [Filecoin CID Checker](https://filecoin.tools/)
- [File.app](https://file.app/)
- [Gliff Explorer](https://explorer.glif.io/)
