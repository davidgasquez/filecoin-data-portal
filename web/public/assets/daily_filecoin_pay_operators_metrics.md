# main.daily_filecoin_pay_operators_metrics

Published daily Filecoin Pay operators metrics.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/daily/filecoin_pay_operators_metrics.sql`
- rows: `344`

## Depends

- `model.fevm_daily_checkpoints`
- `model.filecoin_pay_rail_rate_intervals`

## Tests

- `not_null(date)`
- `not_null(operator)`
- `not_null(active_rails)`
- `not_null(recurring_rails)`
- `not_null(arr_eligible_rails)`
- `not_null(unique_payers)`
- `not_null(unique_payees)`
- `not_null(arr_usdfc)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `date` | `DATE` | UTC date. | `not_null` |
| `operator` | `VARCHAR` | Filecoin Pay operator address. | `not_null` |
| `active_rails` | `BIGINT` | Active rails at end of day. | `not_null` |
| `recurring_rails` | `BIGINT` | Active rails with a positive recurring rate at end of day. | `not_null` |
| `arr_eligible_rails` | `BIGINT` | Active recurring rails counted toward ARR at end of day. | `not_null` |
| `unique_payers` | `BIGINT` | Payers across the operator's active rails at end of day. | `not_null` |
| `unique_payees` | `BIGINT` | Payees across the operator's active rails at end of day. | `not_null` |
| `arr_usdfc` | `DOUBLE` | End-of-day ARR run-rate from the operator's active ARR-eligible rails. | `not_null` |

## Sample (10 rows)

```csv
date,operator,active_rails,recurring_rails,arr_eligible_rails,unique_payers,unique_payees,arr_usdfc
2026-03-03,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,379,244,203,74,16,163.8824376205421
2026-03-06,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,453,342,183,52,16,150.24252436832495
2026-03-30,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,734,601,228,62,16,193.11973647956478
2026-03-13,0x56e53c5e7f27504b810494cc3b88b2aa0645a839,12,7,7,1,10,528.4160343013788
2025-12-03,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,91,78,78,59,10,56.93999999996355
2025-12-18,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,197,137,137,64,15,100.16189185051005
2025-12-19,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,220,148,148,64,16,108.19189185050493
2026-01-15,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,257,173,169,72,15,126.26665882317437
2026-04-12,0x56e53c5e7f27504b810494cc3b88b2aa0645a839,12,8,8,1,10,567.1241597282818
2025-12-12,0x56e53c5e7f27504b810494cc3b88b2aa0645a839,9,7,7,1,8,84.37246850241893
```
