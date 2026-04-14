# beta_filecoin_daily_storage_provider_metrics

Daily Filecoin storage provider metrics from power snapshots, sector lifecycle activity, and verified claims, with sparse provider-day rows.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/beta//filecoin_daily_storage_provider_metrics.sql`
- rows: `5318960`

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
2026-04-14,f01083688,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,3.5,112,1
2026-04-14,f01084788,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,3.1875,102,1
2026-04-14,f01233054,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,3.625,58,1
2026-04-14,f01249,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,0.25,8,1
2026-04-14,f01858258,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,0.34375,11,1
2026-04-14,f02063327,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,0.375,12,1
2026-04-14,f02063867,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,0.375,12,1
2026-04-14,f02620,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,0.5,16,1
2026-04-14,f03230401,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,2.9375,47,1
2026-04-14,f03604724,0.0,0.0,False,0.0,0,0.0,0,0.0,0,0.0,0,4.1875,67,1
```
