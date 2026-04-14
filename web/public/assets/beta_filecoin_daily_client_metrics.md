# beta_filecoin_daily_client_metrics

Daily Filecoin client metrics from verified claims, with sparse client-day rows.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/beta/filecoin_daily_client_metrics.sql`
- rows: `66259`

## Depends

- `raw.verified_registry_claims`

## Tests

- `not_null(date)`
- `not_null(client_id)`
- `not_null(verified_data_onboarded_tibs)`
- `not_null(verified_claims)`
- `not_null(unique_verified_providers)`
- `assert(verified_data_onboarded_tibs > 0)`
- `assert(verified_claims > 0)`
- `assert(unique_verified_providers > 0)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `date` | `DATE` | UTC day when the client had successful verified claims. | `not_null` |
| `client_id` | `VARCHAR` | Filecoin client actor id address. | `not_null` |
| `verified_data_onboarded_tibs` | `DOUBLE` | Sum of verified piece sizes successfully claimed for the client on the day, in tebibytes. | `not_null` |
| `verified_claims` | `BIGINT` | Number of successful verified registry claims for the client on the day. | `not_null` |
| `unique_verified_providers` | `BIGINT` | Distinct providers with at least one successful verified claim for the client on the day. | `not_null` |

## Sample (10 rows)

```csv
date,client_id,verified_data_onboarded_tibs,verified_claims,unique_verified_providers
2026-04-14,f03136439,1.09375,35,3
2026-04-14,f03253574,0.5,16,1
2026-04-14,f03644104,6.6875,214,2
2026-04-14,f03759102,15.125,242,4
2026-04-14,f03768208,0.75,24,2
2026-04-13,f03136439,10.5,336,3
2026-04-13,f03253574,3.5625,114,1
2026-04-13,f03542902,0.34375,11,2
2026-04-13,f03644104,69.71875,2231,2
2026-04-13,f03644598,0.1875,6,4
```
