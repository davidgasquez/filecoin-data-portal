# main.beta_daily_filecoin_pay_operator_metrics

Daily end-of-day Filecoin Pay operator metrics from active rail snapshots, with sparse operator-day rows.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/beta/daily/filecoin_pay_operator_metrics.sql`
- rows: `344`

## Depends

- [`main.foc_filecoin_pay_rail_rate_intervals`](foc_filecoin_pay_rail_rate_intervals.md)
- `raw.fevm_eth_logs_decoded`

## Tests

- `not_null(date)`
- `not_null(operator)`
- `not_null(active_rails)`
- `not_null(active_recurring_rails)`
- `not_null(active_arr_eligible_rails)`
- `not_null(unique_payers)`
- `not_null(unique_payees)`
- `not_null(total_arr_usdfc)`
- `assert(active_rails > 0)`
- `assert(active_recurring_rails >= 0)`
- `assert(active_arr_eligible_rails >= 0)`
- `assert(unique_payers > 0)`
- `assert(unique_payees > 0)`
- `assert(total_arr_usdfc >= 0)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `date` | `DATE` | UTC day for the operator metrics snapshot. | `not_null` |
| `operator` | `VARCHAR` | Filecoin Pay operator address. | `not_null` |
| `active_rails` | `BIGINT` | Distinct active rails managed by the operator at the end of the day. | `not_null` |
| `active_recurring_rails` | `BIGINT` | Distinct active rails with a positive recurring payment rate at the end of the day. | `not_null` |
| `active_arr_eligible_rails` | `BIGINT` | Distinct active recurring rails counted toward USDFC ARR at the end of the day. | `not_null` |
| `unique_payers` | `BIGINT` | Distinct payer wallets across the operator's active rails at the end of the day. | `not_null` |
| `unique_payees` | `BIGINT` | Distinct payee wallets across the operator's active rails at the end of the day. | `not_null` |
| `total_arr_usdfc` | `DOUBLE` | End-of-day USDFC ARR run-rate from the operator's active ARR-eligible recurring rails. | `not_null` |

## Sample (10 rows)

```csv
date,operator,active_rails,active_recurring_rails,active_arr_eligible_rails,unique_payers,unique_payees,total_arr_usdfc
2026-04-15,0x56e53c5e7f27504b810494cc3b88b2aa0645a839,12,8,8,1,10,567.1241597282818
2026-04-15,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,468,362,359,66,16,294.7083920430941
2026-04-15,0xcb71d6e32e12b618f8e0b4dcf36b6a10b5cedc14,1,0,0,1,1,0.0
2026-04-14,0x56e53c5e7f27504b810494cc3b88b2aa0645a839,12,8,8,1,10,567.1241597282818
2026-04-14,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,468,362,359,66,16,294.7071156611649
2026-04-14,0xcb71d6e32e12b618f8e0b4dcf36b6a10b5cedc14,1,0,0,1,1,0.0
2026-04-13,0x56e53c5e7f27504b810494cc3b88b2aa0645a839,12,8,8,1,10,567.1241597282818
2026-04-13,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,452,346,343,66,16,282.56594673751215
2026-04-13,0xcb71d6e32e12b618f8e0b4dcf36b6a10b5cedc14,1,0,0,1,1,0.0
2026-04-12,0x56e53c5e7f27504b810494cc3b88b2aa0645a839,12,8,8,1,10,567.1241597282818
```
