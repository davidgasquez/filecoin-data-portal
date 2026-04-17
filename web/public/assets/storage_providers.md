# main.storage_providers

Published storage providers.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/storage_providers.sql`
- dataset url: `https://data.filecoindataportal.xyz/storage_providers.parquet`
- rows: `8503`

## Depends

- `raw.storage_provider_current_info`
- `model.storage_provider_power_daily`
- `model.storage_provider_sector_lifecycle_daily`
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

## Sample (10 rows)

```csv
provider_id,owner_id,worker_id,peer_id,control_addresses,multi_addresses,sector_size,raw_power_tibs,quality_adjusted_power_tibs,has_power,has_sector_activity,has_verified_claims,first_sector_activity_date,last_sector_activity_date,first_verified_claim_at,last_verified_claim_at,verified_claims,verified_clients,verified_data_onboarded_tibs
f01233054,f03757668,f03756502,12D3KooWFtzeYVUSvGhPpqumswexNwhN2vw12vfaMLb77eDXodxN,"[""f03756503""]","[""/ip4/148.153.245.20/tcp/13004""]",68719476736,1514.0,15140.0,True,True,True,2026-03-03,2026-04-14,2026-03-03 15:37:00+01:00,2026-04-15 01:59:30+02:00,24637,1,1539.8125
f03230401,f03757667,f03756504,12D3KooWRpdDBcZvyDMGH8WLyFwAbJ8HWch1bbW2ShmH3kS99VUF,"[""f03756505""]","[""/ip4/14.238.44.27/tcp/13003""]",68719476736,1462.625,14626.25,True,True,True,2026-03-03,2026-04-14,2026-03-03 15:41:30+01:00,2026-04-15 01:59:00+02:00,23662,1,1478.875
f01084788,f03338164,f03696738,12D3KooWRJi4nBAvjjKhU5L9Tcbzzhr8jr69VpN1j1zDja1G4Zk9,"[""f03696744""]","[""/ip4/15.188.172.88/tcp/4949""]",34359738368,2651.40625,26514.0625,True,True,True,2026-02-11,2026-04-14,2026-02-11 05:36:30+01:00,2026-04-15 01:58:30+02:00,85587,5,2674.59375
f03604724,f01811564,f03604717,12D3KooWDRHr76mnFyZ8YV888iEtPWxhDu8aiLhQvEVPrXMwXQk5,"[""f03604721""]","[""/ip4/42.125.245.71/tcp/30001""]",68719476736,4755.875,47558.75,True,True,True,2025-05-29,2026-04-14,2025-05-29 18:26:00+02:00,2026-04-15 01:58:30+02:00,76989,7,4787.8125
f03605143,f01811564,f03604720,12D3KooWLYDhmYYUnPzqu5nhj7kEuuDKWTdwHdPKUSF41TLXoqsi,"[""f03604721""]","[""/ip4/148.153.188.172/tcp/30002""]",68719476736,4777.6875,47776.875,True,True,True,2025-05-30,2026-04-14,2025-05-30 20:43:00+02:00,2026-04-15 01:57:30+02:00,76859,7,4779.6875
f01083688,f03338164,f03696737,12D3KooWAHTU5Ad25sEr27XXoPUvoQHiahQAzWsTYKt8EZCPeDFB,"[""f03696743""]","[""/ip4/13.58.114.145/tcp/4949""]",34359738368,2490.0625,24900.34375,True,True,True,2025-12-10,2026-04-14,2025-12-10 02:52:30+01:00,2026-04-15 01:55:30+02:00,80608,6,2519.0
f03741653,f03200943,f03741652,Qmaco51xxrAmLZNxPb2r7fdanb6iMyN4oFx8epiHjiv6gS,null,null,34359738368,932.4375,9324.375,True,True,True,2026-02-06,2026-04-14,2026-02-06 17:15:00+01:00,2026-04-15 01:54:00+02:00,29913,1,934.78125
f01858258,f01857658,f03742345,12D3KooWAwbTPeBQEobAavzy5VecX4oBaP1yN8KAXC1t6NhxHY7g,"[""f03742458"", ""f03742461""]","[""/ip4/183.60.248.131/tcp/12888""]",34359738368,3504.625,34970.05596923828,True,True,True,2022-06-10,2026-04-14,2023-03-15 23:22:00+01:00,2026-04-15 01:48:30+02:00,111486,9,3481.1589965820312
f02063867,f02066082,f03742347,12D3KooWP9QL4z6Qsmz6A2Ufmz1oeNiqB1hCLrNjE4jDoo3LBkP9,"[""f03742460"", ""f03742464""]","[""/ip4/183.60.248.132/tcp/14888""]",34359738368,3535.90625,35338.87237548828,True,True,True,2023-03-16,2026-04-14,2023-03-16 10:33:00+01:00,2026-04-15 01:46:30+02:00,112883,9,3524.7254028320312
f01404908,f03500010,f03500011,12D3KooWKZBxKVjP4f5JXw4PvS9unA8cM79Yj4jiF8tuuodm7X1y,"[""f03617552"", ""f03500186""]","[""/dns/cu.00pc.co.kr/tcp/443/wss""]",34359738368,1791.53125,3985.28125,True,True,True,2021-10-29,2026-04-14,2025-06-23 16:19:00+02:00,2026-04-14 20:50:30+02:00,7808,1,243.90625
```
