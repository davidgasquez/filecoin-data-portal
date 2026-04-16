# main.daily_storage_providers_metrics

Published daily metrics for storage providers with power.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/daily/storage_providers_metrics.sql`
- dataset url: `https://data.filecoindataportal.xyz/daily_storage_providers_metrics.parquet`
- rows: `5289036`

## Depends

- `model.storage_provider_power_daily`
- `model.storage_provider_sector_lifecycle_daily`
- `model.daily_verified_claims`

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

## Sample (10 rows)

```csv
date,provider_id,raw_power_tibs,quality_adjusted_power_tibs,onboarded_tibs,onboarded_sectors,terminated_tibs,terminated_sectors,expired_tibs,expired_sectors,removed_tibs,removed_sectors,verified_data_onboarded_tibs,verified_claims,verified_clients
2026-04-14,f02808899,7302.6875,73026.03125,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f02826371,993.21875,9044.0,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f03151456,2532.3125,25317.78125,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f0101021,437.59375,4320.603759765625,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f01106820,1025.34375,1025.34375,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f03066878,229.84375,2298.4375,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f0419414,2035.5,2035.5,0.0,0,0.0,0,57.75,924,57.75,924,0.0,0,0
2026-04-14,f0567188,1032.9375,10322.625,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f03368008,2615.125,26150.6875,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f03573377,4102.53125,41025.3125,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
```
