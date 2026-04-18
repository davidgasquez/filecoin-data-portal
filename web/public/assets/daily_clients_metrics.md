# main.daily_clients_metrics

Published daily clients metrics.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/daily/clients_metrics.sql`
- dataset url: `https://data.filecoindataportal.xyz/daily_clients_metrics.parquet`
- rows: `66198`

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
2026-04-17,f03770592,0.03125,1,1
2026-04-17,f03753456,17.3125,554,1
2026-04-17,f03542902,33.3125,1066,2
2026-04-17,f03759102,78.125,1250,2
2026-04-17,f03510418,4.38690185546875e-05,15,1
2026-04-17,f03644598,1.8125,58,3
2026-04-17,f03644104,46.125,1476,2
2026-04-17,f03535091,12.4375,398,1
2026-04-17,f03253574,2.125,68,1
2026-04-17,f03136439,13.0625,418,3
```
