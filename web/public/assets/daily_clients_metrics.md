# main.daily_clients_metrics

Published daily clients metrics.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/daily/clients_metrics.sql`
- dataset url: `https://data.filecoindataportal.xyz/daily_clients_metrics.parquet`
- rows: `66229`

## Depends

- `model.daily_verified_claims`

## Tests

- `not_null(date)`
- `not_null(client_id)`
- `not_null(verified_data_onboarded_tibs)`
- `not_null(verified_claims)`
- `not_null(verified_providers)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `date` | `DATE` | UTC claim date. | `not_null` |
| `client_id` | `VARCHAR` | Filecoin client actor id address. | `not_null` |
| `verified_data_onboarded_tibs` | `DOUBLE` | Verified data claimed on the date, in tebibytes. | `not_null` |
| `verified_claims` | `HUGEINT` | Successful verified claims on the date. | `not_null` |
| `verified_providers` | `BIGINT` | Providers with at least one successful verified claim on the date. | `not_null` |

## Sample (10 rows)

```csv
date,client_id,verified_data_onboarded_tibs,verified_claims,verified_providers
2026-04-20,f03200311,0.0625,2,2
2026-04-20,f03759102,77.9375,1247,2
2026-04-20,f03644104,1.1875,38,1
2026-04-20,f03644598,0.5,16,2
2026-04-20,f03753456,0.3125,10,1
2026-04-20,f03253574,1.0625,34,1
2026-04-20,f03136439,11.78125,377,3
2026-04-20,f03290407,92.3125,2954,3
2026-04-20,f03535091,0.03125,1,1
2026-04-19,f03290407,101.0,3232,4
```
