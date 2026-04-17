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
2026-04-14,f02063327,3539.46875,35369.85675048828,3.25,104,0.0,0,0.0,0,0.0,0,3.625,116,1
2026-04-14,f02057486,1915.0625,19134.3125,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f02088691,545.5,5359.796875,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f02370792,3551.5,35403.0625,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f02825675,3250.3125,32227.5,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f03134685,125.6875,1234.708984375,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f03315260,6877.21875,68763.46875,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f03378888,2059.625,20596.25,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f03528938,2323.46875,23234.6875,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
2026-04-14,f01083688,2490.0625,24900.34375,50.34375,1611,0.0,0,0.0,0,0.0,0,48.75,1560,2
```
