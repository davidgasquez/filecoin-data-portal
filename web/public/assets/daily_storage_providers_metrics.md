# main.daily_storage_providers_metrics

Published daily storage providers metrics.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/daily/storage_providers_metrics.sql`
- rows: `5319729`

## Depends

- `model.storage_provider_power_daily`
- `model.storage_provider_sector_lifecycle_daily`
- `model.daily_verified_claims`

## Tests

- `not_null(date)`
- `not_null(provider_id)`
- `not_null(raw_power_tibs)`
- `not_null(quality_adjusted_power_tibs)`
- `not_null(has_power)`
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
| `has_power` | `BOOLEAN` | Whether the provider had positive power at end of day. | `not_null` |
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
date,provider_id,raw_power_tibs,quality_adjusted_power_tibs,has_power,onboarded_tibs,onboarded_sectors,terminated_tibs,terminated_sectors,expired_tibs,expired_sectors,removed_tibs,removed_sectors,verified_data_onboarded_tibs,verified_claims,verified_clients
2024-08-13,f03157883,0.0625,0.625,True,37.96875,1215,0.0,0,0.0,0,0.0,0,30.34375,971,1
2024-08-14,f03157883,46.09375,460.9375,True,44.9375,1438,0.0,0,0.0,0,0.0,0,44.59375,1427,1
2024-08-15,f03157883,97.71875,977.1875,True,47.5,1520,0.0,0,0.0,0,0.0,0,49.5,1584,1
2024-08-16,f03157883,150.65625,1506.5625,True,21.59375,691,0.0,0,0.0,0,0.0,0,27.5625,882,2
2024-08-17,f03157883,152.0625,1520.625,True,33.0625,1058,0.0,0,0.0,0,0.0,0,25.34375,811,1
2024-08-18,f03157883,199.1875,1991.875,True,15.53125,497,0.0,0,0.0,0,0.0,0,22.59375,723,1
2024-08-19,f03157883,202.34375,2023.4375,True,30.90625,989,0.0,0,0.0,0,0.0,0,24.03125,769,1
2024-08-20,f03157883,243.84375,2438.4375,True,28.09375,899,0.0,0,0.0,0,0.0,0,28.46875,911,1
2024-08-21,f03157883,288.0,2880.0,True,31.9375,1022,0.0,0,0.0,0,0.0,0,38.53125,1233,1
2024-08-22,f03157883,293.25,2932.5,True,1.6875,54,0.0,0,0.0,0,0.0,0,2.25,72,1
```
