# main.daily_storage_providers_metrics

Published daily metrics for storage providers.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/daily/storage_providers_metrics.sql`
- dataset url: `https://data.filecoindataportal.xyz/daily_storage_providers_metrics.parquet`
- rows: `5325277`

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
2026-04-20,f01002224,386.75,386.75,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,1,1,5.145091729883623,4.7466864730892455
2026-04-20,f0101020,430.90625,4250.213134765625,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,4,4,5.7235833939411584,5.280383188471014
2026-04-20,f0101021,437.59375,4320.603759765625,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,4,4,27.828351192888125,25.67348943624118
2026-04-20,f0101087,2146.78125,2146.7812883257866,0.0,0,0.0,0,6.375,204,6.375,204,0.0,0,0,1,1,7.624631118632032,7.034225100963286
2026-04-20,f01016847,578.28125,5773.53125,0.0,0,0.0,0,0.0625,2,0.0625,2,0.0,0,0,3,3,31.105848112175995,28.69719651652822
2026-04-20,f01019009,601.71875,5990.50390625,0.0,0,0.0,0,0.0625,2,0.0625,2,0.0,0,0,6,6,32.04813371207063,29.566517132296486
2026-04-20,f01021773,1010.75,7388.9375,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,3,3,10.862638291377422,10.021500285459199
2026-04-20,f01045957,1588.1875,1588.1875,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,0,0,0.0,0.0
2026-04-20,f010479,62.625,449.87109375,0.0,0,0.0,0,0.0,0,0.0,0,0.03125,1,1,0,0,0.0,0.0
2026-04-20,f01051151,64.90625,64.90625,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,0,0,0.0,0.0
```
