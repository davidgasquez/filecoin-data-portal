# main.beta_daily_filecoin_storage_providers_metrics

Daily Filecoin storage provider metrics from power snapshots, sector lifecycle activity, and verified claims, with sparse provider-day rows.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/beta/daily/filecoin_storage_providers_metrics.sql`
- rows: `5319729`

## Depends

- `raw.storage_provider_power`
- `raw.storage_provider_sector_lifecycle`
- `raw.storage_provider_verified_claims`

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
- `not_null(unique_verified_clients)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `date` | `DATE` | UTC day for the provider metrics snapshot. | `not_null` |
| `provider_id` | `VARCHAR` | Filecoin storage provider miner actor id address. | `not_null` |
| `raw_power_tibs` | `DOUBLE` | End-of-day raw byte power for the provider, in tebibytes. | `not_null` |
| `quality_adjusted_power_tibs` | `DOUBLE` | End-of-day quality adjusted power for the provider, in tebibytes. | `not_null` |
| `has_power` | `BOOLEAN` | Whether the provider had positive raw or quality adjusted power at end of day. | `not_null` |
| `onboarded_tibs` | `DOUBLE` | Total raw sector data onboarded by the provider on the day, in tebibytes. | `not_null` |
| `onboarded_sectors` | `BIGINT` | Total sectors onboarded by the provider on the day. | `not_null` |
| `terminated_tibs` | `DOUBLE` | Total raw sector data terminated by the provider on the day, in tebibytes. | `not_null` |
| `terminated_sectors` | `BIGINT` | Total sectors terminated by the provider on the day. | `not_null` |
| `expired_tibs` | `DOUBLE` | Total raw sector data expired by the provider on the day, in tebibytes. | `not_null` |
| `expired_sectors` | `BIGINT` | Total sectors expired by the provider on the day. | `not_null` |
| `removed_tibs` | `DOUBLE` | Total raw sector data removed by the provider on the day, in tebibytes. | `not_null` |
| `removed_sectors` | `BIGINT` | Total sectors removed by the provider on the day. | `not_null` |
| `verified_data_onboarded_tibs` | `DOUBLE` | Sum of verified piece sizes claimed by the provider on the day, in tebibytes. | `not_null` |
| `verified_claims` | `BIGINT` | Number of successful verified registry claims by the provider on the day. | `not_null` |
| `unique_verified_clients` | `BIGINT` | Distinct verified clients with at least one successful claim with the provider on the day. | `not_null` |

## Sample (10 rows)

```csv
date,provider_id,raw_power_tibs,quality_adjusted_power_tibs,has_power,onboarded_tibs,onboarded_sectors,terminated_tibs,terminated_sectors,expired_tibs,expired_sectors,removed_tibs,removed_sectors,verified_data_onboarded_tibs,verified_claims,unique_verified_clients
2026-04-15,f01083688,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,5.09375,163,1
2026-04-15,f01084788,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,5.71875,183,1
2026-04-15,f01233054,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,3.3125,53,1
2026-04-15,f01858258,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,0.375,12,1
2026-04-15,f02063867,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,0.375,12,1
2026-04-15,f03230401,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,2.9375,47,1
2026-04-15,f03604724,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,3.6875,59,1
2026-04-15,f03605143,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,4.1875,67,1
2026-04-15,f03741653,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,2.3125,74,1
2026-04-14,f01002224,386.75,386.75,True,0.0,0,0.0,0,0.0,0,0.0,0,0.0,0,0
```
