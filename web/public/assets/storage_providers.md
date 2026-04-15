# main.storage_providers

Published storage providers.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/storage_providers.sql`
- rows: `8870`

## Depends

- `raw.storage_provider_current_info`
- `model.storage_provider_power_daily`
- `model.storage_provider_market_deal_activity`
- `model.storage_provider_sector_lifecycle_daily`
- `model.daily_verified_claims`

## Tests

- `not_null(provider_id)`
- `not_null(has_power)`
- `not_null(has_sector_activity)`
- `not_null(has_market_deals)`
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
| `has_market_deals` | `BOOLEAN` | Whether the provider appears in market deal proposals. | `not_null` |
| `has_verified_claims` | `BOOLEAN` | Whether the provider has successful verified claims. | `not_null` |
| `first_sector_activity_date` | `DATE` | First date with sector lifecycle activity. |  |
| `last_sector_activity_date` | `DATE` | Most recent date with sector lifecycle activity. |  |
| `first_market_deal_start_date` | `DATE` | First observed market deal start date. |  |
| `last_market_deal_start_date` | `DATE` | Most recent market deal start date. |  |
| `first_verified_claim_date` | `DATE` | First date with a successful verified claim. |  |
| `last_verified_claim_date` | `DATE` | Most recent date with a successful verified claim. |  |
| `verified_claims` | `HUGEINT` | Total successful verified claims. |  |
| `verified_clients` | `BIGINT` | Clients with at least one successful verified claim. |  |
| `verified_data_onboarded_tibs` | `DOUBLE` | Verified data successfully claimed, in tebibytes. |  |

## Sample (10 rows)

```csv
provider_id,owner_id,worker_id,peer_id,control_addresses,multi_addresses,sector_size,raw_power_tibs,quality_adjusted_power_tibs,has_power,has_sector_activity,has_market_deals,has_verified_claims,first_sector_activity_date,last_sector_activity_date,first_market_deal_start_date,last_market_deal_start_date,first_verified_claim_date,last_verified_claim_date,verified_claims,verified_clients,verified_data_onboarded_tibs
f095049,f094732,f094733,12D3KooWMrnQ5mFFmjag3CtJ8vtFFhoaW9RcHozRHgQ97HeTso9e,null,"[""/ip4/119.197.20.225/tcp/38833""]",34359738368,null,null,False,True,True,False,2020-12-04,2021-01-02,2020-12-13,2020-12-14,null,null,null,null,null
f09523,f03236,f03236,12D3KooWGEJswpCA5cbXFAGGyiLNR5gcjxKVkEnS5deJUunLwtfZ,null,"[""/ip4/119.161.169.68/tcp/45678"", ""/ip4/8.210.13.50/tcp/45678""]",34359738368,null,null,False,True,True,False,2020-08-27,2020-09-12,2020-08-28,2020-08-30,null,null,null,null,null
f09529,f08247,f08247,12D3KooWNXnBt2Wyw8vs47B683uBVU4BdTjZAj1J9SCoGnT5xCyK,null,null,34359738368,null,null,False,True,True,False,2020-08-27,2020-09-13,2020-08-28,2020-08-30,null,null,null,null,null
f095296,f095219,f095219,12D3KooWRhMMrhArWD88u2Ahrcf2gqvw6oKEZ55Mn1Da7RfEgCa8,null,"[""/ip4/222.187.238.207/tcp/24001""]",34359738368,null,null,False,True,True,False,2020-12-04,2020-12-19,2020-12-07,2020-12-07,null,null,null,null,null
f095334,f01239657,f095330,12D3KooWRM1wv6pR3h9LFrJGArHR1u9Qy2SvADjamftzG15iso9S,"[""f095608""]","[""/ip4/103.65.41.210/tcp/41200""]",34359738368,null,null,False,True,True,False,2020-12-04,2024-05-24,2022-05-01,2022-05-22,null,null,null,null,null
f09537,f09093,f09093,12D3KooWE59P299pvxoExj6Up12CgAqdKCugNNLddEynNDVM4tQf,null,"[""/ip4/47.145.150.94/tcp/1024""]",34359738368,null,null,False,True,True,False,2020-08-31,2020-10-01,2020-09-16,2020-09-16,null,null,null,null,null
f095382,f01220774,f01220846,12D3KooWFpivFBnTWwf621CrbYU5YhJPJWd66wnLWCnvArSFqbYm,"[""f01220873""]",null,34359738368,null,null,False,True,True,False,2020-12-15,2022-08-28,2020-12-21,2020-12-30,null,null,null,null,null
f09555,f09534,f09534,12D3KooWSgwDEohnpgVqYespUqofvMa8sQDFaPkzCqCkDpwJLqAt,"[""f019407""]","[""/ip4/3.25.64.130/tcp/10240""]",34359738368,null,null,False,True,True,False,2020-08-30,2020-09-26,2020-09-03,2020-09-13,null,null,null,null,null
f09559,f09558,f09558,12D3KooWCJwnsMdfcpc7eyMfThFyWxRmsd75pxZiDCbPgZKT6zPG,null,"[""/ip4/99.250.201.0/tcp/31001""]",34359738368,null,null,False,True,True,False,2020-08-27,2020-09-12,2020-08-28,2020-08-29,null,null,null,null,null
f09560,f01035,f01035,12D3KooWF2agZNUZXHfEvHcqwQswaXH9aKRXGWN7FcBvuYLjGk3A,"[""f019557""]","[""/ip4/178.212.192.216/tcp/64002""]",34359738368,null,null,False,True,True,False,2020-08-27,2020-10-21,2020-08-28,2020-09-16,null,null,null,null,null
```
