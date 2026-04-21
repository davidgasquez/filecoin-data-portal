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
| `beneficiary_id` | `VARCHAR` | Current beneficiary actor id address. |  |
| `peer_id` | `VARCHAR` | Current libp2p peer id. |  |
| `control_addresses` | `VARCHAR` | Current JSON array of control addresses. |  |
| `multi_addresses` | `VARCHAR` | Current JSON array of multiaddrs. |  |
| `sector_size` | `BIGINT` | Current sector size in bytes. |  |
| `live_sectors` | `BIGINT` | Current live sector count. |  |
| `active_sectors` | `BIGINT` | Current active sector count. |  |
| `faulty_sectors` | `BIGINT` | Current faulty sector count. |  |
| `actor_balance_fil` | `DOUBLE` | Current miner actor balance, in FIL. |  |
| `available_balance_fil` | `DOUBLE` | Current available miner balance, in FIL. |  |
| `market_escrow_fil` | `DOUBLE` | Current market escrow balance, in FIL. |  |
| `market_locked_fil` | `DOUBLE` | Current market locked balance, in FIL. |  |
| `market_available_fil` | `DOUBLE` | Current market available balance, in FIL. |  |
| `initial_pledge_fil` | `DOUBLE` | Current initial pledge, in FIL. |  |
| `locked_funds_fil` | `DOUBLE` | Current locked funds, in FIL. |  |
| `pre_commit_deposits_fil` | `DOUBLE` | Current pre-commit deposits, in FIL. |  |
| `fee_debt_fil` | `DOUBLE` | Current fee debt, in FIL. |  |
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
provider_id,owner_id,worker_id,beneficiary_id,peer_id,control_addresses,multi_addresses,sector_size,live_sectors,active_sectors,faulty_sectors,actor_balance_fil,available_balance_fil,market_escrow_fil,market_locked_fil,market_available_fil,initial_pledge_fil,locked_funds_fil,pre_commit_deposits_fil,fee_debt_fil,raw_power_tibs,quality_adjusted_power_tibs,has_power,has_sector_activity,has_verified_claims,first_sector_activity_date,last_sector_activity_date,first_verified_claim_at,last_verified_claim_at,verified_claims,verified_clients,verified_data_onboarded_tibs,total_block_rewards_fil
f03230401,f03757667,f03756504,f03757667,12D3KooWRpdDBcZvyDMGH8WLyFwAbJ8HWch1bbW2ShmH3kS99VUF,"[""f03756505""]","[""/ip4/14.238.44.27/tcp/13003""]",68719476736,28097,28077,0,106629.40183548316,4502.461915325389,162.31244126315184,160.81121453620213,1.5012267269497102,101170.86755795049,953.4689454803843,2.603416726898829,0.0,1710.625,17106.25,True,True,True,2026-03-03,2026-04-20,2026-03-03 14:41:30+00:00,2026-04-20 23:59:00+00:00,27676,1,1729.75,1343.1419244480746
f01233054,f03757668,f03756502,f03757668,12D3KooWFtzeYVUSvGhPpqumswexNwhN2vw12vfaMLb77eDXodxN,"[""f03756503""]","[""/ip4/148.153.245.20/tcp/13004""]",68719476736,28429,28341,0,106794.81745312749,3281.5526611038076,162.0341566994051,160.8107467323354,1.2234099670696992,102433.22256262052,1075.5447041283921,4.497525274773359,0.0,1736.5,17365.0,True,True,True,2026-03-03,2026-04-20,2026-03-03 14:37:00+00:00,2026-04-20 23:59:00+00:00,28091,1,1755.6875,1567.825472169063
f01084788,f03338164,f03696738,f03338164,12D3KooWRJi4nBAvjjKhU5L9Tcbzzhr8jr69VpN1j1zDja1G4Zk9,"[""f03696744""]","[""/ip4/15.188.172.88/tcp/4949""]",34359738368,93429,91978,19,201410.7604062164,33902.450699503475,399.67871681582665,241.680451129057,157.99826568676966,165823.22396009945,1681.154608349088,3.9311382643681565,0.0,2654.09375,26540.9375,True,True,True,2026-02-11,2026-04-20,2026-02-11 04:36:30+00:00,2026-04-20 23:55:00+00:00,92582,6,2893.1875,2960.456222207898
f01084868,f03338164,f03759653,f03338164,12D3KooWLGAZMarHVML2KUtY7Hf5H5pfNhXWqCcypqPUYuDeBVFc,"[""f03759650""]","[""/dns/f01084868.44943.com/tcp/443/wss""]",34359738368,691,595,5,49999.93636288813,48733.85907806445,100.0,2.6356554839278195,97.36434451607218,1265.46196364818,0.0,0.6153211755006164,0.0,6.65625,66.5625,True,True,True,2026-04-19,2026-04-20,2026-04-19 15:24:00+00:00,2026-04-20 23:53:30+00:00,453,1,14.15625,0.0
f01858258,f01857658,f03742345,f01857658,12D3KooWAwbTPeBQEobAavzy5VecX4oBaP1yN8KAXC1t6NhxHY7g,"[""f03742458"", ""f03742461""]","[""/ip4/183.60.248.131/tcp/12888""]",34359738368,113186,113147,0,202103.09802221472,861.6897728071317,826.9239675149845,817.7993822834318,9.124585231552715,192977.0640780799,8264.060168567792,0.28400275989493046,0.0,3531.375,35237.55596923828,True,True,True,2022-06-10,2026-04-20,2023-03-15 22:22:00+00:00,2026-04-20 23:50:30+00:00,112341,9,3507.8777465820312,99006.01812773141
f02063327,f02066051,f03742346,f02066051,12D3KooWBWerJoMTuZMgEV9etWiTcgKzYEbrzdj6KYaXQNU8j4vw,"[""f03742459"", ""f03742462""]","[""/ip4/183.60.248.130/tcp/13888""]",34359738368,114040,113943,1,203095.23409091844,158.0631847362463,830.5814801265058,824.4164889707592,6.16499115574652,194739.0255491328,8197.861354289475,0.28400275989493046,0.0,3560.53125,35580.48175048828,True,True,True,2023-03-17,2026-04-20,2023-03-17 19:33:00+00:00,2026-04-20 23:50:30+00:00,113767,9,3552.3972778320312,98732.65323398905
f02063867,f02066082,f03742347,f02066082,12D3KooWP9QL4z6Qsmz6A2Ufmz1oeNiqB1hCLrNjE4jDoo3LBkP9,"[""f03742460"", ""f03742464""]","[""/ip4/183.60.248.132/tcp/14888""]",34359738368,114185,114149,0,204212.83523117393,85.16055254018615,844.2530462152446,833.4484186869654,10.804627528279184,195929.0885294756,8198.302143146575,0.2840060115981865,0.0,3562.53125,35605.12237548828,True,True,True,2023-03-16,2026-04-20,2023-03-16 09:33:00+00:00,2026-04-20 23:48:00+00:00,113738,9,3551.4441528320312,97416.36439583174
f01083688,f03338164,f03696737,f03338164,12D3KooWAHTU5Ad25sEr27XXoPUvoQHiahQAzWsTYKt8EZCPeDFB,"[""f03696743""]","[""/ip4/13.58.114.145/tcp/4949""]",34359738368,86615,85713,12,201043.14264986574,45953.91560842013,396.6570195841273,221.12755202306073,175.52946756106655,153573.09068060032,1512.4845611600035,3.6517996852808734,0.0,2678.53125,26785.03125,True,True,True,2025-12-10,2026-04-20,2025-12-10 01:52:30+00:00,2026-04-20 23:43:30+00:00,86575,7,2705.46875,2745.658514530494
f03741653,f03200943,f03741652,f03286739,Qmaco51xxrAmLZNxPb2r7fdanb6iMyN4oFx8epiHjiv6gS,null,null,34359738368,32766,32766,0,100428.46002028798,42330.83606669807,0.0,0.0,0.0,57594.10425576094,242.39864418416158,261.1210536448001,0.0,1023.9375,10239.375,True,True,True,2026-02-06,2026-04-20,2026-02-06 16:15:00+00:00,2026-04-20 07:55:00+00:00,32767,1,1023.96875,861.0889861733203
f03706409,f03706309,f03706310,f03706309,12D3KooWS8P8mzWVcFPmj63aEtyYEuSaM5xy3HdZu4EepmUHLWYi,"[""f03706311""]","[""/dns/deal.00pc.co.kr/tcp/443/wss""]",68719476736,2080,2071,0,7315.957589071744,10.548020662590986,0.1,0.0,0.1,7167.188533951548,137.55694664046732,0.6640878171377539,0.0,129.4375,1276.1640625,True,True,True,2025-11-29,2026-04-20,2026-01-06 22:16:00+00:00,2026-04-20 07:54:00+00:00,4079,1,127.5390625,252.1975403659064
```
