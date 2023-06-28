# Filecoin Anlytitcs Data Sources

Most of the data required for the dashboards and analysis is coming from the Filecoin chain itself. However, there is some off-chain data like Datacap applications or reputation data that we pull from other places (public and private). This document covers the main data entities and how to get the relavant data.

## Deals

Deals data is available on chain and can be obtained via different ways.

- Doing a `StateMarketDeals` JSON-RPC call and parsing the returned JSON. If you don't have a node running, you can use [Glif nodes](https://lotus.filecoin.io/lotus/developers/glif-nodes/) `StateMarketDeals` periodic dump on S3 ([direct link](https://marketdeals.s3.amazonaws.com/StateMarketDeals.json.zst)).
- Using an [oracle like `fil-naive-marketwatch`](https://github.com/ribasushi/fil-naive-marketwatch).
- Reconstructing the deals state [from Lily](https://lilium.sh/) tables.

This data only shows current state so deals that aren't part of it anymore are not taken into account.

## Clients

Can be derived from the [deals](#deals) table. Clients can be augmented with the following sources:

- Datacap. From Datacap Stats API calling `https://api.datacapstats.io/api/getVerifiedClients` returns a JSON of verified clients in the FIL+ program. This contains the client names, Datacap application data and other self-reported data. Alternatively, this data can be obtained by parsing the relevant GitHub repositories issues and comments.

## Storage Providers

Can be derived from the [deals](#deals) table. Storage Providers cab ve augmented with the following sources:

- Organization names can be derived by linking `miner_id` (Storage Providers) with and Storage Provider Name/Organization in Hubspot. It is represented in the association between the Custom Object _Miner ID_ field _Miner ID_ and the Company Object Associated Company's field _Company Name_.
- Location data from multiple services run by PL or by using the [IP2Location](https://lite.ip2location.com/database/ip-country-region-city) database or similar.
- Reputation datafrom [filrep.io](https://filrep.io/) or internal sources.
- More Storage Providers details using the different [provider.quest](https://provider.quest/) endpoints.

## Others

- [Storage Market](https://data.storage.market/)
