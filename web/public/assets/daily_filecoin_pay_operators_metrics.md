# main.daily_filecoin_pay_operators_metrics

Published daily Filecoin Pay operators metrics.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/daily/filecoin_pay_operators_metrics.sql`
- dataset url: `https://data.filecoindataportal.xyz/daily_filecoin_pay_operators_metrics.parquet`
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
2026-04-15,0xcb71d6e32e12b618f8e0b4dcf36b6a10b5cedc14,1,0,0,1,1,0.0
2026-04-15,0x56e53c5e7f27504b810494cc3b88b2aa0645a839,12,8,8,1,10,567.1241597282818
2026-04-15,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,476,370,367,66,16,300.9943493820897
2026-04-14,0xcb71d6e32e12b618f8e0b4dcf36b6a10b5cedc14,1,0,0,1,1,0.0
2026-04-14,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,468,362,359,66,16,294.7083920430942
2026-04-14,0x56e53c5e7f27504b810494cc3b88b2aa0645a839,12,8,8,1,10,567.1241597282818
2026-04-13,0xcb71d6e32e12b618f8e0b4dcf36b6a10b5cedc14,1,0,0,1,1,0.0
2026-04-13,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,452,346,343,66,16,282.5671678369944
2026-04-13,0x56e53c5e7f27504b810494cc3b88b2aa0645a839,12,8,8,1,10,567.1241597282818
2026-04-12,0x56e53c5e7f27504b810494cc3b88b2aa0645a839,12,8,8,1,10,567.1241597282818
```
