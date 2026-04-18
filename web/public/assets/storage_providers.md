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
f01233054,f03757668,f03756502,12D3KooWFtzeYVUSvGhPpqumswexNwhN2vw12vfaMLb77eDXodxN,"[""f03756503""]","[""/ip4/148.153.245.20/tcp/13004""]",68719476736,1631.4375,16314.375,True,True,True,2026-03-03,2026-04-17,2026-03-03 14:37:00+00:00,2026-04-17 23:59:30+00:00,26421,1,1651.3125,1379.9974798419753
f03230401,f03757667,f03756504,12D3KooWRpdDBcZvyDMGH8WLyFwAbJ8HWch1bbW2ShmH3kS99VUF,"[""f03756505""]","[""/ip4/14.238.44.27/tcp/13003""]",68719476736,1579.875,15798.75,True,True,True,2026-03-03,2026-04-17,2026-03-03 14:41:30+00:00,2026-04-17 23:59:30+00:00,25600,1,1600.0,1209.887795584926
f01084788,f03338164,f03696738,12D3KooWRJi4nBAvjjKhU5L9Tcbzzhr8jr69VpN1j1zDja1G4Zk9,"[""f03696744""]","[""/ip4/15.188.172.88/tcp/4949""]",34359738368,2735.0625,27350.625,True,True,True,2026-02-11,2026-04-17,2026-02-11 04:36:30+00:00,2026-04-17 23:51:30+00:00,88177,5,2755.53125,2711.9225877899403
f01083688,f03338164,f03696737,12D3KooWAHTU5Ad25sEr27XXoPUvoQHiahQAzWsTYKt8EZCPeDFB,"[""f03696743""]","[""/ip4/13.58.114.145/tcp/4949""]",34359738368,2560.65625,25606.28125,True,True,True,2025-12-10,2026-04-17,2025-12-10 01:52:30+00:00,2026-04-17 23:50:30+00:00,82826,6,2588.3125,2456.942502124922
f01858258,f01857658,f03742345,12D3KooWAwbTPeBQEobAavzy5VecX4oBaP1yN8KAXC1t6NhxHY7g,"[""f03742458"", ""f03742461""]","[""/ip4/183.60.248.131/tcp/12888""]",34359738368,3518.0625,35104.43096923828,True,True,True,2022-06-10,2026-04-17,2023-03-15 22:22:00+00:00,2026-04-17 23:49:30+00:00,111909,9,3494.3777465820312,98646.6651057716
f02063327,f02066051,f03742346,12D3KooWBWerJoMTuZMgEV9etWiTcgKzYEbrzdj6KYaXQNU8j4vw,"[""f03742459"", ""f03742462""]","[""/ip4/183.60.248.130/tcp/13888""]",34359738368,3551.09375,35486.10675048828,True,True,True,2023-03-17,2026-04-17,2023-03-17 19:33:00+00:00,2026-04-17 23:49:30+00:00,113464,9,3542.9285278320312,98276.03089470208
f02063867,f02066082,f03742347,12D3KooWP9QL4z6Qsmz6A2Ufmz1oeNiqB1hCLrNjE4jDoo3LBkP9,"[""f03742460"", ""f03742464""]","[""/ip4/183.60.248.132/tcp/14888""]",34359738368,3549.375,35473.55987548828,True,True,True,2023-03-16,2026-04-17,2023-03-16 09:33:00+00:00,2026-04-17 23:47:00+00:00,113307,9,3537.9754028320312,97067.1243726708
f03741653,f03200943,f03741652,Qmaco51xxrAmLZNxPb2r7fdanb6iMyN4oFx8epiHjiv6gS,null,null,34359738368,972.4375,9724.375,True,True,True,2026-02-06,2026-04-17,2026-02-06 16:15:00+00:00,2026-04-17 15:58:00+00:00,31119,1,972.46875,738.7067926597589
f03644168,f03632590,f03644165,12D3KooWQKTq2derMYzNrRhwZsrRRCc47GLkX1WS2hvbq3oFbdct,"[""f03644177"", ""f03644178"", ""f03644179"", ""f03644180"", ""f03644181"", ""f03644182""]","[""/dns/a-fil-http.aur.lu/tcp/443/wss""]",34359738368,2287.96875,14554.1953125,True,True,True,2025-10-08,2025-12-20,2025-10-10 12:50:30+00:00,2026-04-17 15:28:30+00:00,43614,5,1362.9140625,5136.790890342636
f03623017,f03632590,f03622985,12D3KooWJLEqAUExUULbfFagCDXwTVabndyVcr3LnvkA8SmYr1Hv,"[""f03622994"", ""f03622995"", ""f03622988"", ""f03622989"", ""f03622990"", ""f03622997""]","[""/dns/p-fil-http.aur.lu/tcp/443/wss""]",34359738368,928.0,1948.09375,True,True,True,2025-07-31,2025-08-20,2025-08-25 16:03:30+00:00,2026-04-17 15:12:30+00:00,3627,5,113.34375,1494.4671956883774
```
