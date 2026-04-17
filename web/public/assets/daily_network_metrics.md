# main.daily_network_metrics

Published daily network metrics.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/daily/network_metrics.sql`
- dataset url: `https://data.filecoindataportal.xyz/daily_network_metrics.parquet`
- rows: `2062`

## Depends

- `model.daily_network_activity`
- `model.daily_sector_lifecycle`
- `model.daily_verified_claims`
- `model.daily_filecoin_pay_arr`
- `model.warm_storage_daily_activity`
- `raw.coincodex_filecoin_market_data`
- `raw.daily_network_power`

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
| `raw_power_pibs` | `DOUBLE` | End-of-day raw byte power, in pebibytes. |  |
| `quality_adjusted_power_pibs` | `DOUBLE` | End-of-day quality adjusted power, in pebibytes. |  |
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
date,transactions,onboarded_pibs,terminated_pibs,expired_pibs,removed_pibs,raw_power_pibs,quality_adjusted_power_pibs,gas_used_millions,total_value_fil,total_gas_fee_fil,total_value_flow_fil,active_payers,active_datasets,new_payers,new_datasets,arr_usdfc,fil_token_price_avg_usd,fil_token_volume_usd,fil_token_market_cap_usd,verified_data_onboarded_pibs,verified_claims,verified_clients,verified_providers
2026-04-16,44730,0.161224365234375,7.24835205078125,1.150543212890625,8.398895263671875,1964.8703918457031,16992.981124240905,4010609.764604002,18651901.751644233,1.660075621,18651903.411719854,65,370,0,0,868.1185091103713,0.9749660260698291,293013611.82229966,752923968.1219512,0.14740003366023302,3684,8,15
2026-04-15,46055,0.135345458984375,0.00250244140625,0.79522705078125,0.7977294921875,1970.8576354980469,16968.61627534707,4404365.999548002,8067222.504011742,1.202536326,8067223.706548068,65,370,0,8,868.1160884891668,0.9033965821729063,172803026.80487806,697470630.4076655,0.15518190246075392,3203,8,16
2026-04-14,49282,0.28973388671875,0.00054931640625,0.320892333984375,0.321441650390625,1977.2680053710938,17034.2975027528,5915929.666035999,11408211.587484161,1.691876669,11408213.279360830,65,362,0,16,861.8312753894467,0.8986038041033811,214183747.40069687,693470157.0487804,0.28790283203125,6711,8,17
2026-04-13,45055,0.258880615234375,3.0517578125e-05,3.08563232421875,3.085662841796875,1970.029541015625,16962.452660004812,10602474.273976998,12624167.061212949,2.188581270,12624169.249794219,65,346,0,13,849.690106465794,0.872909142464586,160236225.41463414,673504658.5017421,0.25885009765625,5621,10,17
2026-04-12,41393,0.25982666015625,0.0,3.71014404296875,3.71014404296875,1965.0768127441406,16911.509658647905,5254004.722119,9296796.503247193,1.443164622,9296797.946411815,65,623,0,0,839.7544884478411,0.8680431622787766,189386117.9512195,669538898.7735192,0.263275146484375,5758,7,16
2026-04-11,41786,0.2708740234375,3.0517578125e-05,2.26739501953125,2.267425537109375,1969.6727905273438,16954.187906191888,5701138.53858,7323158.380762169,1.421976075,7323159.802738244,65,626,0,0,839.1241641515006,0.9025515661257371,154128106.4703833,695983857.7909408,0.26611328125,6006,6,14
2026-04-10,63157,0.263671875,0.00018310546875,0.9664306640625,0.96661376953125,1974.984130859375,16997.612481599877,9776180.57874,11290432.002370237,2.356807469,11290434.359177706,65,702,1,1,839.0774061393491,0.9069125153413455,165317231.19512194,697813157.076655,0.2651500701904297,6271,7,15
2026-04-09,44696,0.29437255859375,0.0,0.72943115234375,0.72943115234375,1984.7205505371094,17056.66205241179,7942773.928979001,11659267.220217598,2.257414998,11659269.477632596,64,703,0,1,839.0218390668025,0.888151559082019,157767908.8466899,683318744.0034844,0.2946796417236328,6844,9,17
2026-04-08,45610,0.230438232421875,0.0235595703125,0.821502685546875,0.845062255859375,1984.8153686523438,17053.22151479099,8779491.747283999,10187912.159084491,1.736075362,10187913.895159853,64,702,1,2,837.8547743895218,0.9024174547937743,257476681.32857144,694213177.0642858,0.22247314453125,6039,8,14
2026-04-07,43270,0.216644287109375,0.017059326171875,0.475128173828125,0.4921875,1987.9056701660156,17081.0580733658,7845375.569438,8421672.060161604,1.959910165,8421674.020071769,63,700,0,2,836.3523754083673,0.8636731080963166,221541228.85614035,664285828.1789473,0.21166992373764515,5690,9,16
```
