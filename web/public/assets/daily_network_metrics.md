# main.daily_network_metrics

Published daily network metrics.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/daily/network_metrics.sql`
- dataset url: `https://data.filecoindataportal.xyz/daily_network_metrics.parquet`
- rows: `2061`

## Depends

- `model.daily_network_activity`
- `model.daily_sector_lifecycle`
- `model.daily_verified_claims`
- `model.daily_filecoin_pay_arr`
- `model.warm_storage_daily_activity`
- `raw.coincodex_filecoin_market_data`

## Tests

- `not_null(date)`
- `unique(date)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `date` | `DATE` | UTC date. | `not_null`, `unique` |
| `transactions` | `HUGEINT` | Onchain transactions. |  |
| `onboarded_pibs` | `DOUBLE` | Raw sector data onboarded on the date, in pebibytes. |  |
| `terminated_pibs` | `DOUBLE` | Raw sector data terminated on the date, in pebibytes. |  |
| `expired_pibs` | `DOUBLE` | Raw sector data expired on the date, in pebibytes. |  |
| `removed_pibs` | `DOUBLE` | Raw sector data removed on the date, in pebibytes. |  |
| `gas_used_millions` | `DOUBLE` | Total gas used, in millions. |  |
| `total_value_fil` | `DECIMAL(38,9)` | FIL transferred by top-level messages. |  |
| `total_gas_fee_fil` | `DECIMAL(38,9)` | FIL paid in gas fees. |  |
| `total_value_flow_fil` | `DECIMAL(38,9)` | FIL value transferred plus gas fees. |  |
| `active_payers` | `BIGINT` | Payers with at least one active chargeable warm storage dataset. |  |
| `active_datasets` | `BIGINT` | Active chargeable warm storage datasets. |  |
| `new_payers` | `BIGINT` | Payers whose first chargeable warm storage dataset started billing on the date. |  |
| `new_datasets` | `BIGINT` | Warm storage datasets whose billing started on the date. |  |
| `arr_usdfc` | `DOUBLE` | End-of-day ARR run-rate from active ARR-eligible rails. |  |
| `fil_token_price_avg_usd` | `DOUBLE` | Average FIL price in USD. |  |
| `fil_token_volume_usd` | `DOUBLE` | FIL trading volume in USD. |  |
| `fil_token_market_cap_usd` | `DOUBLE` | FIL market capitalization in USD. |  |
| `verified_data_onboarded_pibs` | `DOUBLE` | Verified data claimed on the date, in pebibytes. |  |
| `verified_claims` | `HUGEINT` | Successful verified claims on the date. |  |
| `verified_clients` | `BIGINT` | Clients with at least one successful verified claim on the date. |  |
| `verified_providers` | `BIGINT` | Providers with at least one successful verified claim on the date. |  |

## Sample (10 rows)

```csv
date,transactions,onboarded_pibs,terminated_pibs,expired_pibs,removed_pibs,gas_used_millions,total_value_fil,total_gas_fee_fil,total_value_flow_fil,active_payers,active_datasets,new_payers,new_datasets,arr_usdfc,fil_token_price_avg_usd,fil_token_volume_usd,fil_token_market_cap_usd,verified_data_onboarded_pibs,verified_claims,verified_clients,verified_providers
2026-04-15,0,0.0,0.0,0.0,0.0,0.0,0E-9,0E-9,0E-9,65,362,0,0,861.8325517713756,0.9033965821729063,172803026.80487806,697470630.4076655,0.02734375,670,4,9
2026-04-14,49282,0.28973388671875,0.00054931640625,0.320892333984375,0.321441650390625,5915929.666035999,11408211.587484161,1.691876669,11408213.279360830,65,362,0,16,861.8312753894465,0.8986038041033811,214183747.40069687,693470157.0487804,0.28790283203125,6711,8,17
2026-04-13,45055,0.258880615234375,3.0517578125e-05,3.08563232421875,3.085662841796875,10602474.273976998,12624167.061212949,2.188581270,12624169.249794219,65,346,0,13,849.690106465794,0.872909142464586,160236225.41463414,673504658.5017421,0.25885009765625,5621,10,17
2026-04-12,41393,0.25982666015625,0.0,3.71014404296875,3.71014404296875,5254004.722119,9296796.503247193,1.443164622,9296797.946411815,65,623,0,0,839.7544884478409,0.8680431622787766,189386117.9512195,669538898.7735192,0.263275146484375,5758,7,16
2026-04-11,41786,0.2708740234375,3.0517578125e-05,2.26739501953125,2.267425537109375,5701138.53858,7323158.380762169,1.421976075,7323159.802738244,65,626,0,0,839.1241641515006,0.9025515661257371,154128106.4703833,695983857.7909408,0.26611328125,6006,6,14
2026-04-10,63157,0.263671875,0.00018310546875,0.9664306640625,0.96661376953125,9776180.57874,11290432.002370237,2.356807469,11290434.359177706,65,702,1,1,839.0774061393491,0.9069125153413455,165317231.19512194,697813157.076655,0.2651500701904297,6271,7,15
2026-04-09,44696,0.29437255859375,0.0,0.72943115234375,0.72943115234375,7942773.928979001,11659267.220217598,2.257414998,11659269.477632596,64,703,0,1,839.0218390668025,0.888151559082019,157767908.8466899,683318744.0034844,0.2946796417236328,6844,9,17
2026-04-08,45610,0.230438232421875,0.0235595703125,0.821502685546875,0.845062255859375,8779491.747283999,10187912.159084491,1.736075362,10187913.895159853,64,702,1,2,837.8547743895218,0.9024174547937743,257476681.32857144,694213177.0642858,0.22247314453125,6039,8,14
2026-04-07,43270,0.216644287109375,0.017059326171875,0.475128173828125,0.4921875,7845375.569438,8421672.060161604,1.959910165,8421674.020071769,63,700,0,2,836.352375408367,0.8636731080963166,221541228.85614035,664285828.1789473,0.21166992373764515,5690,9,16
2026-04-06,42334,0.1998291015625,0.0,0.717926025390625,0.717926025390625,4777059.251076,12183335.442023532,1.810973845,12183337.252997377,63,698,0,5,834.4577923303831,0.8676983243269454,204483339.85365853,667304517.8571428,0.19964599609375,5295,7,14
```
