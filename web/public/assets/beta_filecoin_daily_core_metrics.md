# beta_filecoin_daily_core_metrics

Daily mainnet Filecoin core metrics.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/beta/filecoin_daily_core_metrics.sql`
- rows: `162`

## Depends

- `raw.fevm_eth_logs_decoded`
- `raw.foc_filecoin_warm_storage_datasets`
- `raw.foc_filecoin_pay_rail_rate_intervals`
- `raw.daily_network_activity_by_method`
- `raw.daily_sector_lifecycle`

## Tests

- `not_null(date)`
- `not_null(total_active_payers)`
- `not_null(total_active_datasets)`
- `not_null(new_active_payers)`
- `not_null(new_active_datasets)`
- `not_null(total_arr_usdfc)`
- `not_null(sector_onboarded_pibs)`
- `not_null(sector_terminated_pibs)`
- `not_null(sector_expired_pibs)`
- `not_null(sector_removed_pibs)`
- `not_null(gas_used_millions)`
- `not_null(transactions)`
- `not_null(total_value_fil)`
- `not_null(total_gas_fee_fil)`
- `not_null(total_value_flow_fil)`
- `unique(date)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `date` | `DATE` | UTC day for the metric snapshot. | `not_null`, `unique` |
| `total_active_payers` | `BIGINT` | Distinct payers with at least one chargeable warm storage dataset active on the day. | `not_null` |
| `total_active_datasets` | `BIGINT` | Distinct chargeable warm storage datasets active on the day. | `not_null` |
| `new_active_payers` | `BIGINT` | Distinct payers whose first-ever chargeable warm storage dataset began billing on the day. | `not_null` |
| `new_active_datasets` | `BIGINT` | Distinct warm storage datasets whose billing started on the day. | `not_null` |
| `total_arr_usdfc` | `DOUBLE` | End-of-day USDFC ARR run-rate from active recurring Filecoin Pay rails. | `not_null` |
| `sector_onboarded_pibs` | `DOUBLE` | Raw sector bytes onboarded that day, in pebibytes. | `not_null` |
| `sector_terminated_pibs` | `DOUBLE` | Raw sector bytes terminated that day, in pebibytes. Before 2026-01-16 this also includes expirations. | `not_null` |
| `sector_expired_pibs` | `DOUBLE` | Raw sector bytes expired that day, in pebibytes. | `not_null` |
| `sector_removed_pibs` | `DOUBLE` | Raw sector bytes removed that day from termination or expiration, in pebibytes. | `not_null` |
| `gas_used_millions` | `DOUBLE` | Total gas used across all onchain methods that day, in millions of gas units. | `not_null` |
| `transactions` | `HUGEINT` | Total onchain transactions that day. | `not_null` |
| `total_value_fil` | `DECIMAL(38,9)` | Total FIL value transferred by top-level messages that day. | `not_null` |
| `total_gas_fee_fil` | `DECIMAL(38,9)` | Total FIL paid in gas fees that day, including base fee burn, overestimation burn, and miner tips. | `not_null` |
| `total_value_flow_fil` | `DECIMAL(38,9)` | Total FIL value flow that day, defined as top-level message value plus gas fees. | `not_null` |

## Sample (10 rows)

```csv
date,total_active_payers,total_active_datasets,new_active_payers,new_active_datasets,total_arr_usdfc,sector_onboarded_pibs,sector_terminated_pibs,sector_expired_pibs,sector_removed_pibs,gas_used_millions,transactions,total_value_fil,total_gas_fee_fil,total_value_flow_fil
2026-04-14,65,346,0,0,849.6913275652773,0.0,0.0,0.0,0.0,0.0,0,0E-9,0E-9,0E-9
2026-04-13,65,346,0,13,849.6901064657951,0.258880615234375,3.0517578125e-05,3.08563232421875,3.085662841796875,10602474.273976998,45055,12624167.061212949,2.188581270,12624169.249794219
2026-04-12,65,623,0,0,839.7544884478423,0.25982666015625,0.0,3.71014404296875,3.71014404296875,5254004.722119,41393,9296796.503247193,1.443164622,9296797.946411815
2026-04-11,65,626,0,0,839.1241641515018,0.2708740234375,3.0517578125e-05,2.26739501953125,2.267425537109375,5701138.53858,41786,7323158.380762169,1.421976075,7323159.802738244
2026-04-10,65,702,1,1,839.0774061393502,0.263671875,0.00018310546875,0.9664306640625,0.96661376953125,9776180.57874,63157,11290432.002370237,2.356807469,11290434.359177706
2026-04-09,64,703,0,1,839.0218390668036,0.29437255859375,0.0,0.72943115234375,0.72943115234375,7942773.928979001,44696,11659267.220217598,2.257414998,11659269.477632596
2026-04-08,64,702,1,2,837.854774389523,0.230438232421875,0.0235595703125,0.821502685546875,0.845062255859375,8779491.747283999,45610,10187912.159084491,1.736075362,10187913.895159853
2026-04-07,63,700,0,2,836.3523754083684,0.216644287109375,0.017059326171875,0.475128173828125,0.4921875,7845375.569438,43270,8421672.060161604,1.959910165,8421674.020071769
2026-04-06,63,698,0,5,834.4577923303842,0.1998291015625,0.0,0.717926025390625,0.717926025390625,4777059.251076,42334,12183335.442023532,1.810973845,12183337.252997377
2026-04-05,63,693,0,10,830.3484915681787,0.19488525390625,0.000885009765625,0.656219482421875,0.6571044921875,5632617.578043998,39155,6545600.398771181,1.830592766,6545602.229363947
```
