# main.storage_providers

Published storage providers.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/storage_providers.sql`
- dataset url: `https://data.filecoindataportal.xyz/storage_providers.parquet`
- rows: `8505`

## Depends

- `raw.storage_provider_current_info`
- `model.storage_provider_power_daily`
- `model.storage_provider_sector_lifecycle_daily`
- `model.storage_provider_block_rewards_daily`
- `raw.verified_registry_claims`

## Tests

- `not_null(provider_id)`
- `not_null(has_power)`
- `not_null(has_sector_activity)`
- `not_null(has_verified_claims)`
- `unique(provider_id)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `provider_id` | `VARCHAR` | Filecoin storage provider actor id address. | `not_null`, `unique` |
| `owner_id` | `VARCHAR` | Current owner actor id address. |  |
| `worker_id` | `VARCHAR` | Current worker actor id address. |  |
| `peer_id` | `VARCHAR` | Current libp2p peer id. |  |
| `control_addresses` | `VARCHAR` | Current JSON array of control addresses. |  |
| `multi_addresses` | `VARCHAR` | Current JSON array of multiaddrs. |  |
| `sector_size` | `BIGINT` | Current sector size in bytes. |  |
| `raw_power_tibs` | `DOUBLE` | Current raw byte power, in tebibytes. |  |
| `quality_adjusted_power_tibs` | `DOUBLE` | Current quality adjusted power, in tebibytes. |  |
| `has_power` | `BOOLEAN` | Whether the provider currently has positive power. | `not_null` |
| `has_sector_activity` | `BOOLEAN` | Whether the provider has sector lifecycle activity. | `not_null` |
| `has_verified_claims` | `BOOLEAN` | Whether the provider has successful verified claims. | `not_null` |
| `first_sector_activity_date` | `DATE` | First date with sector lifecycle activity. |  |
| `last_sector_activity_date` | `DATE` | Most recent date with sector lifecycle activity. |  |
| `first_verified_claim_at` | `TIMESTAMP WITH TIME ZONE` | First successful verified claim timestamp. |  |
| `last_verified_claim_at` | `TIMESTAMP WITH TIME ZONE` | Most recent successful verified claim timestamp. |  |
| `verified_claims` | `BIGINT` | Total successful verified claims. |  |
| `verified_clients` | `BIGINT` | Clients with at least one successful verified claim. |  |
| `verified_data_onboarded_tibs` | `DOUBLE` | Verified data successfully claimed, in tebibytes. |  |
| `total_block_rewards_fil` | `DOUBLE` | Total block rewards allocated to the provider, in FIL. |  |

## Sample (10 rows)

```csv
provider_id,owner_id,worker_id,peer_id,control_addresses,multi_addresses,sector_size,raw_power_tibs,quality_adjusted_power_tibs,has_power,has_sector_activity,has_verified_claims,first_sector_activity_date,last_sector_activity_date,first_verified_claim_at,last_verified_claim_at,verified_claims,verified_clients,verified_data_onboarded_tibs,total_block_rewards_fil
f01233054,f03757668,f03756502,12D3KooWFtzeYVUSvGhPpqumswexNwhN2vw12vfaMLb77eDXodxN,"[""f03756503""]","[""/ip4/148.153.245.20/tcp/13004""]",68719476736,1701.0,17010.0,True,True,True,2026-03-03,2026-04-19,2026-03-03 14:37:00+00:00,2026-04-19 23:59:00+00:00,27536,1,1721.0,1487.5730926004362
f03230401,f03757667,f03756504,12D3KooWRpdDBcZvyDMGH8WLyFwAbJ8HWch1bbW2ShmH3kS99VUF,"[""f03756505""]","[""/ip4/14.238.44.27/tcp/13003""]",68719476736,1667.4375,16674.375,True,True,True,2026-03-03,2026-04-19,2026-03-03 14:41:30+00:00,2026-04-19 23:58:00+00:00,26984,1,1686.5,1317.2516501306707
f01083688,f03338164,f03696737,12D3KooWAHTU5Ad25sEr27XXoPUvoQHiahQAzWsTYKt8EZCPeDFB,"[""f03696743""]","[""/ip4/13.58.114.145/tcp/4949""]",34359738368,2648.5625,26485.34375,True,True,True,2025-12-10,2026-04-19,2025-12-10 01:52:30+00:00,2026-04-19 23:56:00+00:00,85599,7,2674.96875,2647.6578566335725
f03706409,f03706309,f03706310,12D3KooWS8P8mzWVcFPmj63aEtyYEuSaM5xy3HdZu4EepmUHLWYi,"[""f03706311""]","[""/dns/deal.00pc.co.kr/tcp/443/wss""]",68719476736,125.375,1235.5390625,True,True,True,2025-11-29,2026-04-19,2026-01-06 22:16:00+00:00,2026-04-19 23:55:00+00:00,4045,1,126.4765625,252.1975403659064
f01084788,f03338164,f03696738,12D3KooWRJi4nBAvjjKhU5L9Tcbzzhr8jr69VpN1j1zDja1G4Zk9,"[""f03696744""]","[""/ip4/15.188.172.88/tcp/4949""]",34359738368,2527.03125,25270.3125,True,True,True,2026-02-11,2026-04-19,2026-02-11 04:36:30+00:00,2026-04-19 23:50:30+00:00,90901,6,2840.65625,2898.3622638808033
f01858258,f01857658,f03742345,12D3KooWAwbTPeBQEobAavzy5VecX4oBaP1yN8KAXC1t6NhxHY7g,"[""f03742458"", ""f03742461""]","[""/ip4/183.60.248.131/tcp/12888""]",34359738368,3526.84375,35192.24346923828,True,True,True,2022-06-10,2026-04-19,2023-03-15 22:22:00+00:00,2026-04-19 23:50:00+00:00,112197,9,3503.3777465820312,98902.38621963633
f02063867,f02066082,f03742347,12D3KooWP9QL4z6Qsmz6A2Ufmz1oeNiqB1hCLrNjE4jDoo3LBkP9,"[""f03742460"", ""f03742464""]","[""/ip4/183.60.248.132/tcp/14888""]",34359738368,3558.15625,35561.37237548828,True,True,True,2023-03-16,2026-04-19,2023-03-16 09:33:00+00:00,2026-04-19 23:47:30+00:00,113595,9,3546.9754028320312,97327.88871642001
f01084868,f03338164,f03759653,12D3KooWLGAZMarHVML2KUtY7Hf5H5pfNhXWqCcypqPUYuDeBVFc,"[""f03759650""]","[""/dns/f01084868.44943.com/tcp/443/wss""]",34359738368,null,null,False,True,True,2026-04-19,2026-04-19,2026-04-19 15:24:00+00:00,2026-04-19 23:45:00+00:00,108,1,3.375,0.0
f03623017,f03632590,f03622985,12D3KooWJLEqAUExUULbfFagCDXwTVabndyVcr3LnvkA8SmYr1Hv,"[""f03622994"", ""f03622995"", ""f03622988"", ""f03622989"", ""f03622990"", ""f03622997""]","[""/dns/p-fil-http.aur.lu/tcp/443/wss""]",34359738368,928.0,1950.0625,True,True,True,2025-07-31,2025-08-20,2025-08-25 16:03:30+00:00,2026-04-19 22:24:30+00:00,3634,5,113.5625,1496.757909441575
f03741653,f03200943,f03741652,Qmaco51xxrAmLZNxPb2r7fdanb6iMyN4oFx8epiHjiv6gS,null,null,34359738368,1023.90625,10239.0625,True,True,True,2026-02-06,2026-04-19,2026-02-06 16:15:00+00:00,2026-04-19 12:37:30+00:00,32766,1,1023.9375,826.1319002632008
```
