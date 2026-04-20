# main.daily_storage_providers_metrics

Published daily metrics for storage providers.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/daily/storage_providers_metrics.sql`
- dataset url: `https://data.filecoindataportal.xyz/daily_storage_providers_metrics.parquet`
- rows: `5324514`

## Depends

- `model.storage_provider_power_daily`
- `model.storage_provider_sector_lifecycle_daily`
- `model.storage_provider_block_rewards_daily`
- `model.daily_verified_claims`
- `raw.coincodex_filecoin_market_data`

## Tests

- `not_null(date)`
- `not_null(provider_id)`
- `not_null(raw_power_tibs)`
- `not_null(quality_adjusted_power_tibs)`
- `not_null(onboarded_tibs)`
- `not_null(onboarded_sectors)`
- `not_null(terminated_tibs)`
- `not_null(terminated_sectors)`
- `not_null(expired_tibs)`
- `not_null(expired_sectors)`
- `not_null(removed_tibs)`
- `not_null(removed_sectors)`
- `not_null(verified_data_onboarded_tibs)`
- `not_null(verified_claims)`
- `not_null(verified_clients)`
- `not_null(blocks_mined)`
- `not_null(win_count)`
- `not_null(block_rewards_fil)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `date` | `DATE` | UTC date. | `not_null` |
| `provider_id` | `VARCHAR` | Filecoin storage provider actor id address. | `not_null` |
| `raw_power_tibs` | `DOUBLE` | End-of-day raw byte power, in tebibytes. | `not_null` |
| `quality_adjusted_power_tibs` | `DOUBLE` | End-of-day quality adjusted power, in tebibytes. | `not_null` |
| `onboarded_tibs` | `DOUBLE` | Raw data onboarded on the date, in tebibytes. | `not_null` |
| `onboarded_sectors` | `BIGINT` | Sectors onboarded on the date. | `not_null` |
| `terminated_tibs` | `DOUBLE` | Raw data terminated on the date, in tebibytes. | `not_null` |
| `terminated_sectors` | `BIGINT` | Sectors terminated on the date. | `not_null` |
| `expired_tibs` | `DOUBLE` | Raw data expired on the date, in tebibytes. | `not_null` |
| `expired_sectors` | `BIGINT` | Sectors expired on the date. | `not_null` |
| `removed_tibs` | `DOUBLE` | Raw data removed on the date, in tebibytes. | `not_null` |
| `removed_sectors` | `BIGINT` | Sectors removed on the date. | `not_null` |
| `verified_data_onboarded_tibs` | `DOUBLE` | Verified data claimed on the date, in tebibytes. | `not_null` |
| `verified_claims` | `HUGEINT` | Successful verified claims on the date. | `not_null` |
| `verified_clients` | `BIGINT` | Clients with at least one successful verified claim on the date. | `not_null` |
| `blocks_mined` | `BIGINT` | Block headers mined by the provider on the date. | `not_null` |
| `win_count` | `BIGINT` | Winning proofs recorded by the provider on the date. | `not_null` |
| `block_rewards_fil` | `DOUBLE` | Exact block rewards allocated to the provider on the date, in FIL. | `not_null` |
| `block_rewards_usd` | `DOUBLE` | Exact block rewards allocated to the provider on the date, valued with the daily average FIL price, in USD. |  |

## Sample (10 rows)

```csv
date,provider_id,raw_power_tibs,quality_adjusted_power_tibs,onboarded_tibs,onboarded_sectors,terminated_tibs,terminated_sectors,expired_tibs,expired_sectors,removed_tibs,removed_sectors,verified_data_onboarded_tibs,verified_claims,verified_clients,blocks_mined,win_count,block_rewards_fil,block_rewards_usd
2026-04-19,f01002224,386.75,386.75,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,1,1,2.746765632258809,2.5397836619285337
2026-04-19,f0101020,430.90625,4250.213134765625,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,8,8,30.06086688983488,27.79563632716127
2026-04-19,f0101021,437.59375,4320.603759765625,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,4,4,21.862627460225642,20.21517357658541
2026-04-19,f0101087,2153.15625,2153.1562883257866,0.0,0,0.0,0,6.53125,209,6.53125,209,0.0,0,0,1,1,4.577920194721947,4.232951941591777
2026-04-19,f01016847,578.28125,5773.53125,0.0,0,0.0,0,0.03125,1,0.03125,1,0.0,0,0,5,5,16.084440434207714,14.872400668734715
2026-04-19,f01019009,601.78125,5991.12890625,0.0,0,0.0,0,0.09375,3,0.09375,3,0.0,0,0,3,3,11.11665542837981,10.278962100261161
2026-04-19,f01021773,1010.75,7388.9375,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,7,7,32.68195260328903,30.219210655223158
2026-04-19,f01045957,1588.1875,1588.1875,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,2,2,7.928861317241057,7.33138357154476
2026-04-19,f010479,62.625,449.58984375,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,2,2,7.845951856419318,7.254721736424451
2026-04-19,f01051151,64.90625,64.90625,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,0,0,0.0,0.0
```
