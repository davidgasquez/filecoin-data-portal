# Data Sources

Most of the data required for dashboards and analysis is coming from the Filecoin chain. However, there is some off-chain data like Datacap applications or reputation data that we need to pull from several places.

This document goes over the different entities and the data sources we use to get the data.

## Deals

Deals data is available on chain and can be obtained via a `StateMarketDeals` JSON-RPC call. That said, is easirt to use an [oracle like `fil-naive-marketwatch`](https://github.com/ribasushi/fil-naive-marketwatch).

You can also get the data from the [Glif nodes](https://lotus.filecoin.io/lotus/developers/glif-nodes/) `StateMarketDeals` periodic dump on S3 ([direct link](https://marketdeals.s3.amazonaws.com/StateMarketDeals.json.zst)) or [from Lily](https://lilium.sh/).

## Clients

Can be derived from all the historical deals on-chain. Then augmented with the following sources:

- Datacap Stats API. E.g: calling `https://api.datacapstats.io/api/getVerifiedClients` returns a JSON of verified clients in the FIL+ program. This contains the client names and other self-reported data.
    - This can also be obtained by parsing the relevant GitHub repositories issues and comments.

## Storage Providers

Can be derived from all the historical deals on-chain. Then augmented with the following sources:

- Using the different [provider.quest](https://provider.quest/) endpoints.
- Location data from multiple services run by PL.
- The best source for linking `miner_id` (Storage Providers) with and Storage Provider Name/Organization is Hubspot. It is represented in the association between the Custom Object _Miner ID_ field _Miner ID_ and the Company Object Associated Company's field _Company Name_.
- Reputation datafrom [filrep.io](https://filrep.io/) or internal sources.

## Others

- [Storage Market](https://data.storage.market/)
