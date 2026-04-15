# main.beta_daily_filecoin_clients_metrics

Daily Filecoin client metrics from verified claims, with sparse client-day rows.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/beta/daily/filecoin_clients_metrics.sql`
- rows: `66266`

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
2026-04-15,f03136439,0.75,24,2
2026-04-15,f03535091,2.3125,74,1
2026-04-15,f03644104,10.8125,346,2
2026-04-15,f03759102,14.125,226,4
2026-04-14,f03136439,12.59375,403,3
2026-04-14,f03253574,7.28125,233,2
2026-04-14,f03542902,0.0625,2,1
2026-04-14,f03644104,101.40625,3245,2
2026-04-14,f03644598,0.15625,5,3
2026-04-14,f03759102,170.1875,2723,4
```
