# main.daily_network_metrics

Published daily network metrics.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/daily/network_metrics.sql`
- rows: `2061`

## Depends

- `model.daily_network_activity`
- `model.daily_sector_lifecycle`
- `model.daily_verified_claims`
- `model.daily_filecoin_pay_arr`
- `model.warm_storage_daily_activity`

## Tests

- `not_null(date)`
- `not_null(transactions)`
- `not_null(onboarded_pibs)`
- `not_null(terminated_pibs)`
- `not_null(expired_pibs)`
- `not_null(removed_pibs)`
- `not_null(gas_used_millions)`
- `not_null(total_value_fil)`
- `not_null(total_gas_fee_fil)`
- `not_null(total_value_flow_fil)`
- `not_null(active_payers)`
- `not_null(active_datasets)`
- `not_null(new_payers)`
- `not_null(new_datasets)`
- `not_null(arr_usdfc)`
- `not_null(verified_data_onboarded_pibs)`
- `not_null(verified_claims)`
- `not_null(verified_clients)`
- `not_null(verified_providers)`
- `unique(date)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `date` | `DATE` | UTC date. | `not_null`, `unique` |
| `transactions` | `HUGEINT` | Onchain transactions. | `not_null` |
| `onboarded_pibs` | `DOUBLE` | Raw sector data onboarded on the date, in pebibytes. | `not_null` |
| `terminated_pibs` | `DOUBLE` | Raw sector data terminated on the date, in pebibytes. | `not_null` |
| `expired_pibs` | `DOUBLE` | Raw sector data expired on the date, in pebibytes. | `not_null` |
| `removed_pibs` | `DOUBLE` | Raw sector data removed on the date, in pebibytes. | `not_null` |
| `gas_used_millions` | `DOUBLE` | Total gas used, in millions. | `not_null` |
| `total_value_fil` | `DECIMAL(38,9)` | FIL transferred by top-level messages. | `not_null` |
| `total_gas_fee_fil` | `DECIMAL(38,9)` | FIL paid in gas fees. | `not_null` |
| `total_value_flow_fil` | `DECIMAL(38,9)` | FIL value transferred plus gas fees. | `not_null` |
| `active_payers` | `BIGINT` | Payers with at least one active chargeable warm storage dataset. | `not_null` |
| `active_datasets` | `BIGINT` | Active chargeable warm storage datasets. | `not_null` |
| `new_payers` | `BIGINT` | Payers whose first chargeable warm storage dataset started billing on the date. | `not_null` |
| `new_datasets` | `BIGINT` | Warm storage datasets whose billing started on the date. | `not_null` |
| `arr_usdfc` | `DOUBLE` | End-of-day ARR run-rate from active ARR-eligible rails. | `not_null` |
| `verified_data_onboarded_pibs` | `DOUBLE` | Verified data claimed on the date, in pebibytes. | `not_null` |
| `verified_claims` | `HUGEINT` | Successful verified claims on the date. | `not_null` |
| `verified_clients` | `BIGINT` | Clients with at least one successful verified claim on the date. | `not_null` |
| `verified_providers` | `BIGINT` | Providers with at least one successful verified claim on the date. | `not_null` |

## Sample (10 rows)

```csv
date,transactions,onboarded_pibs,terminated_pibs,expired_pibs,removed_pibs,gas_used_millions,total_value_fil,total_gas_fee_fil,total_value_flow_fil,active_payers,active_datasets,new_payers,new_datasets,arr_usdfc,verified_data_onboarded_pibs,verified_claims,verified_clients,verified_providers
2020-08-24,3,0.0703125,0.0,0.0,0.0,47.566226,0E-9,0.000008924,0.000008924,0,0,0,0,0.0,0.0,0,0,0
2020-08-25,747469,8.47509765625,0.0003662109375,0.0,0.0003662109375,18045945.936328005,3247071.352013752,351.363582837,3247422.715596589,0,0,0,0,0.0,0.0,0,0,0
2020-08-26,923813,10.897674560546875,0.00201416015625,0.0,0.00201416015625,24076459.904601,2008122.801279855,3.995834483,2008126.797114338,0,0,0,0,0.0,0.0,0,0,0
2020-08-27,1016010,11.707763671875,0.001922607421875,0.0,0.001922607421875,25666897.296399992,1402969.952665195,1.011207109,1402970.963872304,0,0,0,0,0.0,0.0,0,0,0
2020-08-28,1019616,11.96453857421875,0.0028076171875,0.0,0.0028076171875,27803889.394512013,2690365.373076407,3642.908236280,2694008.281312687,0,0,0,0,0.0,0.0,0,0,0
2020-08-29,869775,11.60675048828125,0.0023193359375,0.0,0.0023193359375,25810499.916686006,953143.632456359,1576348.036203792,2529491.668660151,0,0,0,0,0.0,0.0,0,0,0
2020-08-30,985591,11.5291748046875,0.001129150390625,0.0,0.001129150390625,26296469.950428005,1194611.375879421,49938.977821921,1244550.353701342,0,0,0,0,0.0,0.0,0,0,0
2020-08-31,891276,11.51904296875,0.0003662109375,0.0,0.0003662109375,26103576.845503002,1534386.316522368,84515.873795058,1618902.190317426,0,0,0,0,0.0,0.0,0,0,0
2020-09-01,876103,12.00299072265625,0.00042724609375,0.0,0.00042724609375,26673383.754689,769061.714633861,13517.090325061,782578.804958922,0,0,0,0,0.0,0.0,0,0,0
2020-09-02,1069940,11.272369384765625,0.00360107421875,0.0,0.00360107421875,25741092.691957995,1426957.892655064,625301.176369839,2052259.069024903,0,0,0,0,0.0,0.0,0,0,0
```
