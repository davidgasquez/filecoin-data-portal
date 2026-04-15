# main.beta_filecoin_storage_providers

Historically active Filecoin storage providers enriched with current miner info, current power, market deal activity, and verified claim activity.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/beta/filecoin_storage_providers.sql`
- rows: `8870`

## Depends

- `raw.storage_provider_current_info`
- `raw.storage_provider_current_power`
- `raw.storage_provider_market_deal_activity`
- `raw.storage_provider_sector_lifecycle`
- `raw.storage_provider_verified_claims`

## Tests

- `not_null(provider_id)`
- `not_null(has_current_power)`
- `not_null(has_sector_activity)`
- `not_null(has_market_deals)`
- `not_null(has_verified_claims)`
- `unique(provider_id)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `provider_id` | `VARCHAR` | Filecoin storage provider miner actor id address. | `not_null`, `unique` |
| `owner_id` | `VARCHAR` | Current owner id address from the latest Lily miner info snapshot, if available. |  |
| `worker_id` | `VARCHAR` | Current worker id address from the latest Lily miner info snapshot, if available. |  |
| `peer_id` | `VARCHAR` | Current libp2p peer id from the latest Lily miner info snapshot, if available. |  |
| `control_addresses` | `VARCHAR` | Current JSON array of control addresses from the latest Lily miner info snapshot, if available. |  |
| `multi_addresses` | `VARCHAR` | Current JSON array of multiaddrs from the latest Lily miner info snapshot, if available. |  |
| `sector_size` | `BIGINT` | Current sector size in bytes from the latest Lily miner info snapshot, if available. |  |
| `current_raw_power_tibs` | `DOUBLE` | Latest observed raw byte power for the provider, in tebibytes, if currently positive. |  |
| `current_quality_adjusted_power_tibs` | `DOUBLE` | Latest observed quality adjusted power for the provider, in tebibytes, if currently positive. |  |
| `has_current_power` | `BOOLEAN` | Whether the provider currently has positive raw or quality adjusted power. | `not_null` |
| `has_sector_activity` | `BOOLEAN` | Whether the provider has at least one sector lifecycle event in the provider daily sector lifecycle table. | `not_null` |
| `has_market_deals` | `BOOLEAN` | Whether the provider appears in Lily market deal proposals. | `not_null` |
| `has_verified_claims` | `BOOLEAN` | Whether the provider has at least one successful verified claim. | `not_null` |
| `first_sector_activity_date` | `DATE` | First day with sector lifecycle activity for the provider, if available. |  |
| `last_sector_activity_date` | `DATE` | Most recent day with sector lifecycle activity for the provider, if available. |  |
| `first_market_deal_start_date` | `DATE` | First observed storage deal start date for the provider, if available. |  |
| `last_market_deal_start_date` | `DATE` | Most recent storage deal start date for the provider, if available. |  |
| `first_verified_claim_date` | `DATE` | First day with a successful verified claim for the provider, if available. |  |
| `last_verified_claim_date` | `DATE` | Most recent day with a successful verified claim for the provider, if available. |  |
| `total_verified_claims` | `HUGEINT` | Total successful verified claims observed for the provider. |  |
| `total_verified_data_onboarded_tibs` | `DOUBLE` | Total verified data successfully claimed by the provider, in tebibytes. |  |

## Sample (10 rows)

```csv
provider_id,owner_id,worker_id,peer_id,control_addresses,multi_addresses,sector_size,current_raw_power_tibs,current_quality_adjusted_power_tibs,has_current_power,has_sector_activity,has_market_deals,has_verified_claims,first_sector_activity_date,last_sector_activity_date,first_market_deal_start_date,last_market_deal_start_date,first_verified_claim_date,last_verified_claim_date,total_verified_claims,total_verified_data_onboarded_tibs
f01000,f0100,f0100,12D3KooWGuQafP1HDkE2ixXZnX6q6LLygsUG1uoxaQEtfPAt5ygp,null,null,34359738368,null,null,False,True,False,False,2020-08-24,2020-09-29,null,null,null,null,null,null
f0100033,f02054722,f02017170,12D3KooWEyKFjW6ii86YUtNTRJaXDEZRUey5SyisJTBBj3bJWvai,"[""f02018095""]",null,34359738368,null,null,False,True,False,False,2020-12-10,2023-01-17,null,null,null,null,null,null
f0100034,f0410211,f0100003,12D3KooWKJYQN8PVR3iXZt9iZQMRoBhcah16ihaydF8AhoUBVFum,"[""f0100059""]",null,34359738368,null,null,False,True,False,False,2021-01-25,2022-07-31,null,null,null,null,null,null
f010005,f010004,f010004,12D3KooWM8fTYQMxEygkYaf6atg9EkDeaoYKo5JKbxsZLE9CNcgU,null,null,34359738368,null,null,False,False,True,False,null,null,2020-09-02,2020-09-03,null,null,null,null
f0100050,f099688,f0100032,12D3KooWHvCY5kgkrWr98dJHEzsDwJeKc9Ha4HnsMMetoL6iF1vk,"[""f0101743""]","[""/ip4/118.46.119.62/tcp/24001""]",34359738368,null,null,False,True,True,False,2020-12-10,2021-01-06,2020-12-14,2020-12-14,null,null,null,null
f0100066,f0100061,f0100057,12D3KooWQeGjrB32dTuVrxuWcEEFN9WzfZR2vVzniWewxw5MMWyr,"[""f0100057""]",null,34359738368,null,null,False,True,False,False,2020-12-09,2025-01-22,null,null,null,null,null,null
f0100082,f052509,f0100081,12D3KooWKbnTrct6FM4Yw4nhN91tQfSUPAk9tJjKv3T9e2z3RZ4V,"[""f023836""]","[""/ip4/221.163.91.162/tcp/32342""]",34359738368,null,null,False,True,True,False,2020-12-24,2025-10-01,2021-03-09,2022-02-03,null,null,null,null
f010009,f01237,f01237,12D3KooWJsVPnwRZAPq1k3shaM58AUuNvy43MrBmWFHBDsBNVuPK,null,null,34359738368,null,null,False,True,True,False,2020-08-28,2020-09-12,2020-08-29,2020-08-30,null,null,null,null
f01001,f0101,f0101,12D3KooWBoi3uudz9WLmw1zdk87Uu5w3RdAzc3EYBB8YYKx2mefG,null,null,34359738368,null,null,False,True,False,False,2020-08-24,2020-10-29,null,null,null,null,null,null
f010010,f07720,f07720,12D3KooWJKscJmPde3MdvDnxxVeySZfBpkbyXMf2Si8ivfQoMJNh,"[""f022819""]","[""/ip4/61.177.78.101/tcp/9981""]",34359738368,null,null,False,True,True,False,2020-08-28,2023-03-20,2020-08-29,2021-03-08,null,null,null,null
```
