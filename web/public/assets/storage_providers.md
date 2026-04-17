# main.storage_providers

Published storage providers.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/storage_providers.sql`
- dataset url: `https://data.filecoindataportal.xyz/storage_providers.parquet`
- rows: `8504`

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
f03230401,f03757667,f03756504,12D3KooWRpdDBcZvyDMGH8WLyFwAbJ8HWch1bbW2ShmH3kS99VUF,"[""f03756505""]","[""/ip4/14.238.44.27/tcp/13003""]",68719476736,1536.6875,15366.875,True,True,True,2026-03-03,2026-04-16,2026-03-03 14:41:30+00:00,2026-04-16 23:58:00+00:00,24906,1,1556.625,1128.4741090749453
f01233054,f03757668,f03756502,12D3KooWFtzeYVUSvGhPpqumswexNwhN2vw12vfaMLb77eDXodxN,"[""f03756503""]","[""/ip4/148.153.245.20/tcp/13004""]",68719476736,1596.6875,15966.875,True,True,True,2026-03-03,2026-04-16,2026-03-03 14:37:00+00:00,2026-04-16 23:57:30+00:00,25865,1,1616.5625,1317.9293657115666
f01084788,f03338164,f03696738,12D3KooWRJi4nBAvjjKhU5L9Tcbzzhr8jr69VpN1j1zDja1G4Zk9,"[""f03696744""]","[""/ip4/15.188.172.88/tcp/4949""]",34359738368,1068.28125,10682.8125,True,True,True,2026-02-11,2026-04-16,2026-02-11 04:36:30+00:00,2026-04-16 23:56:30+00:00,86506,5,2703.3125,2656.0559610171263
f01083688,f03338164,f03696737,12D3KooWAHTU5Ad25sEr27XXoPUvoQHiahQAzWsTYKt8EZCPeDFB,"[""f03696743""]","[""/ip4/13.58.114.145/tcp/4949""]",34359738368,1435.8125,14358.125,True,True,True,2025-12-10,2026-04-16,2025-12-10 01:52:30+00:00,2026-04-16 23:55:00+00:00,81404,6,2543.875,2413.780884076267
f03741653,f03200943,f03741652,Qmaco51xxrAmLZNxPb2r7fdanb6iMyN4oFx8epiHjiv6gS,null,null,34359738368,950.53125,9505.3125,True,True,True,2026-02-06,2026-04-16,2026-02-06 16:15:00+00:00,2026-04-16 23:52:00+00:00,30721,1,960.03125,711.2066144472865
f03706409,f03706309,f03706310,12D3KooWS8P8mzWVcFPmj63aEtyYEuSaM5xy3HdZu4EepmUHLWYi,"[""f03706311""]","[""/dns/deal.00pc.co.kr/tcp/443/wss""]",68719476736,118.75,1169.2890625,True,True,True,2025-11-29,2026-04-16,2026-01-06 22:16:00+00:00,2026-04-16 23:50:00+00:00,3811,1,119.1640625,235.26731560965118
f02063327,f02066051,f03742346,12D3KooWBWerJoMTuZMgEV9etWiTcgKzYEbrzdj6KYaXQNU8j4vw,"[""f03742459"", ""f03742462""]","[""/ip4/183.60.248.130/tcp/13888""]",34359738368,3546.59375,35441.10675048828,True,True,True,2023-03-17,2026-04-16,2023-03-17 19:33:00+00:00,2026-04-16 23:49:30+00:00,113320,9,3538.4285278320312,98144.13694938249
f01858258,f01857658,f03742345,12D3KooWAwbTPeBQEobAavzy5VecX4oBaP1yN8KAXC1t6NhxHY7g,"[""f03742458"", ""f03742461""]","[""/ip4/183.60.248.131/tcp/12888""]",34359738368,3513.59375,35059.74346923828,True,True,True,2022-06-10,2026-04-16,2023-03-15 22:22:00+00:00,2026-04-16 23:49:00+00:00,111772,9,3490.0964965820312,98498.66120388923
f02063867,f02066082,f03742347,12D3KooWP9QL4z6Qsmz6A2Ufmz1oeNiqB1hCLrNjE4jDoo3LBkP9,"[""f03742460"", ""f03742464""]","[""/ip4/183.60.248.132/tcp/14888""]",34359738368,3544.875,35428.55987548828,True,True,True,2023-03-16,2026-04-16,2023-03-16 09:33:00+00:00,2026-04-16 23:47:00+00:00,113170,9,3533.6941528320312,96898.47292543
f01081439,f03338164,f03759651,12D3KooWNZ1bNnLikm84dXC4oSWcBX9TEPUAV7Bx2PUpryWmWv8a,"[""f03759648""]","[""/dns/f01081439.44943.com/tcp/443/wss""]",34359738368,null,null,False,True,True,2026-04-16,2026-04-16,2026-04-16 23:42:00+00:00,2026-04-16 23:42:00+00:00,5,1,0.15625,0.0
```
