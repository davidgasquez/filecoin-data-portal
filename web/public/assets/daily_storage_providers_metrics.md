# main.daily_storage_providers_metrics

Published daily metrics for storage providers.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/daily/storage_providers_metrics.sql`
- dataset url: `https://data.filecoindataportal.xyz/daily_storage_providers_metrics.parquet`
- rows: `5322978`

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
2026-04-17,f01002224,386.75,386.75,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,0,0,0.0,0.0
2026-04-17,f0101020,430.90625,4250.213134765625,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,4,4,22.916761136201675,22.76194100898648
2026-04-17,f0101021,437.59375,4320.603759765625,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,2,2,9.854241268180937,9.787668383920302
2026-04-17,f0101087,2166.28125,2166.2812883257866,0.0,0,0.0,0,1.25,40,1.25,40,0.0,0,0,1,1,5.728955448295837,5.690252002985923
2026-04-17,f01016847,578.40625,5774.78125,0.0,0,0.0,0,0.03125,1,0.03125,1,0.0,0,0,4,4,14.8682764775049,14.767829977144878
2026-04-17,f01019009,601.9375,5992.69140625,0.0,0,0.0,0,0.0625,2,0.0625,2,0.0,0,0,5,5,25.825842031219985,25.6513688530536
2026-04-17,f01021773,1010.75,7388.9375,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,3,3,15.714146596808698,15.607985601337443
2026-04-17,f01045957,1588.1875,1588.1875,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,1,1,5.49957883525872,5.462425003186014
2026-04-17,f010479,23.625,171.0,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,0,0,0.0,0.0
2026-04-17,f01051151,64.90625,64.90625,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0,0,0,0.0,0.0
```
