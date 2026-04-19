# main.daily_clients_metrics

Published daily clients metrics.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/daily/clients_metrics.sql`
- dataset url: `https://data.filecoindataportal.xyz/daily_clients_metrics.parquet`
- rows: `66210`

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
2026-04-18,f03290407,47.96875,1535,2
2026-04-18,f03136439,13.5,432,3
2026-04-18,f03535091,29.1875,934,1
2026-04-18,f03644104,4.40625,141,2
2026-04-18,f03644598,0.65625,21,3
2026-04-18,f03753456,11.71875,375,1
2026-04-18,f03253574,6.09375,195,2
2026-04-18,f03183111,9.03125,289,1
2026-04-18,f03759102,78.125,1250,2
2026-04-18,f03542902,10.9375,350,2
```
