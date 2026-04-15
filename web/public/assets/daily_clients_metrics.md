# main.daily_clients_metrics

Published daily clients metrics.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/daily/clients_metrics.sql`
- rows: `66266`

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
2023-07-25,f02128612,5.3125,170,2
2025-06-29,f03523911,163.78125,5241,5
2023-09-15,f02224404,134.59375,2604,6
2025-06-24,f03045127,40.40625,1293,2
2025-04-19,f03535034,186.875,5980,5
2024-12-20,f03196570,3.4375,110,1
2025-03-19,f03239735,28.0,896,2
2023-04-30,f02084354,137.705078125,4418,9
2025-01-27,f03139932,46.0,1472,3
2023-04-22,f01987869,42.90625,1373,3
```
