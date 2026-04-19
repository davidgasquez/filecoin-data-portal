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
f01233054,f03757668,f03756502,12D3KooWFtzeYVUSvGhPpqumswexNwhN2vw12vfaMLb77eDXodxN,"[""f03756503""]","[""/ip4/148.153.245.20/tcp/13004""]",68719476736,1666.1875,16661.875,True,True,True,2026-03-03,2026-04-18,2026-03-03 14:37:00+00:00,2026-04-18 23:59:30+00:00,26979,1,1686.1875,1434.8644832472298
f01083688,f03338164,f03696737,12D3KooWAHTU5Ad25sEr27XXoPUvoQHiahQAzWsTYKt8EZCPeDFB,"[""f03696743""]","[""/ip4/13.58.114.145/tcp/4949""]",34359738368,2604.1875,26041.59375,True,True,True,2025-12-10,2026-04-18,2025-12-10 01:52:30+00:00,2026-04-18 23:59:30+00:00,84210,7,2631.5625,2562.766775554676
f03741653,f03200943,f03741652,Qmaco51xxrAmLZNxPb2r7fdanb6iMyN4oFx8epiHjiv6gS,null,null,34359738368,993.40625,9934.0625,True,True,True,2026-02-06,2026-04-18,2026-02-06 16:15:00+00:00,2026-04-18 23:59:30+00:00,32053,1,1001.65625,778.6744157552291
f03230401,f03757667,f03756504,12D3KooWRpdDBcZvyDMGH8WLyFwAbJ8HWch1bbW2ShmH3kS99VUF,"[""f03756505""]","[""/ip4/14.238.44.27/tcp/13003""]",68719476736,1624.125,16241.25,True,True,True,2026-03-03,2026-04-18,2026-03-03 14:41:30+00:00,2026-04-18 23:58:00+00:00,26292,1,1643.25,1255.0355127080204
f01404908,f03500010,f03500011,12D3KooWKZBxKVjP4f5JXw4PvS9unA8cM79Yj4jiF8tuuodm7X1y,"[""f03617552"", ""f03500186""]","[""/dns/cu.00pc.co.kr/tcp/443/wss""]",34359738368,1801.1875,4081.84375,True,True,True,2021-10-29,2026-04-18,2025-06-23 14:19:00+00:00,2026-04-18 23:55:00+00:00,8132,1,254.03125,17032.19905299346
f01084788,f03338164,f03696738,12D3KooWRJi4nBAvjjKhU5L9Tcbzzhr8jr69VpN1j1zDja1G4Zk9,"[""f03696744""]","[""/ip4/15.188.172.88/tcp/4949""]",34359738368,2767.15625,27671.5625,True,True,True,2026-02-11,2026-04-18,2026-02-11 04:36:30+00:00,2026-04-18 23:50:30+00:00,89186,6,2787.0625,2813.8082475490633
f02063327,f02066051,f03742346,12D3KooWBWerJoMTuZMgEV9etWiTcgKzYEbrzdj6KYaXQNU8j4vw,"[""f03742459"", ""f03742462""]","[""/ip4/183.60.248.130/tcp/13888""]",34359738368,3555.59375,35531.10675048828,True,True,True,2023-03-17,2026-04-18,2023-03-17 19:33:00+00:00,2026-04-18 23:50:00+00:00,113608,9,3547.4285278320312,98431.91005807673
f01858258,f01857658,f03742345,12D3KooWAwbTPeBQEobAavzy5VecX4oBaP1yN8KAXC1t6NhxHY7g,"[""f03742458"", ""f03742461""]","[""/ip4/183.60.248.131/tcp/12888""]",34359738368,3522.4375,35148.18096923828,True,True,True,2022-06-10,2026-04-18,2023-03-15 22:22:00+00:00,2026-04-18 23:49:30+00:00,112053,9,3498.8777465820312,98780.26339436273
f02063867,f02066082,f03742347,12D3KooWP9QL4z6Qsmz6A2Ufmz1oeNiqB1hCLrNjE4jDoo3LBkP9,"[""f03742460"", ""f03742464""]","[""/ip4/183.60.248.132/tcp/14888""]",34359738368,3553.6875,35516.68487548828,True,True,True,2023-03-16,2026-04-18,2023-03-16 09:33:00+00:00,2026-04-18 23:47:30+00:00,113451,9,3542.4754028320312,97207.63040358751
f02011071,f02011061,f02011065,12D3KooWE8pscBxgq6Wcxti66Hv4QVvp2RUP4dMTJYQ6xFKT4rjM,"[""f03515493"", ""f03515497"", ""f03515494"", ""f03515492""]","[""/dns/fc6000.sf.archive.org/tcp/443/wss""]",34359738368,456.96875,4546.645144462585,True,True,True,2023-01-26,2026-04-18,2023-01-26 02:05:00+00:00,2026-04-18 23:40:30+00:00,15865,4,485.85380268096924,2938.752098664435
```
