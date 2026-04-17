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
- `model.network_block_rewards_by_height`
- `raw.coincodex_filecoin_market_data`
- `raw.daily_network_power`
- `raw.daily_protocol_revenue`

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
| `protocol_revenue_fil` | `DECIMAL(38,9)` | Daily protocol revenue from burned FIL, in FIL. |  |
| `protocol_revenue_usd` | `DOUBLE` | Daily protocol revenue from burned FIL, in USD. |  |
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
| `blocks_mined` | `HUGEINT` | Block headers mined on the date. |  |
| `win_count` | `HUGEINT` | Winning proofs recorded on the date. |  |
| `block_rewards_fil` | `DOUBLE` | Exact block rewards minted on the date, in FIL. |  |
| `block_rewards_usd` | `DOUBLE` | Exact block rewards minted on the date, valued with the daily average FIL price, in USD. |  |
| `block_rewards_fil_per_qap_tib_day` | `DOUBLE` | Exact block rewards minted on the date per 1 TiB of network quality adjusted power, in FIL. |  |
| `block_rewards_usd_per_qap_tib_day` | `DOUBLE` | Exact block rewards minted on the date per 1 TiB of network quality adjusted power, in USD. |  |
| `reward_per_wincount_fil` | `DOUBLE` | Exact reward allocated per win count on the date, in FIL. |  |

## Sample (10 rows)

```csv
date,transactions,onboarded_pibs,terminated_pibs,expired_pibs,removed_pibs,raw_power_pibs,quality_adjusted_power_pibs,gas_used_millions,total_value_fil,total_gas_fee_fil,total_value_flow_fil,protocol_revenue_fil,protocol_revenue_usd,active_payers,active_datasets,new_payers,new_datasets,arr_usdfc,fil_token_price_avg_usd,fil_token_volume_usd,fil_token_market_cap_usd,verified_data_onboarded_pibs,verified_claims,verified_clients,verified_providers,blocks_mined,win_count,block_rewards_fil,block_rewards_usd,block_rewards_fil_per_qap_tib_day,block_rewards_usd_per_qap_tib_day,reward_per_wincount_fil
2026-04-16,44730,0.161224365234375,7.24835205078125,1.150543212890625,8.398895263671875,1964.8703918457031,16992.981124240905,4010609.764604002,18651901.751644233,1.660075621,18651903.411719854,5074.300629965,4947.270720280606,0,0,0,0,0.0,0.9749660260698291,293013611.82229966,752923968.1219512,0.16085829306393862,4128,10,16,14153,14246,65325.01131652958,63689.66668624346,0.0037541356573859057,0.003660154723208582,4.585498477925704
2026-04-15,46055,0.135345458984375,0.00250244140625,0.79522705078125,0.7977294921875,1970.8576354980469,16968.61627534707,4404365.999548002,8067222.504011742,1.202536326,8067223.706548068,1744.474032462,1575.9518786155584,65,370,0,8,868.1185091103721,0.9033965821729063,172803026.80487806,697470630.4076655,0.13543705642223358,2711,8,17,14151,14259,65446.18299631383,59123.85803513249,0.0037664996983397506,0.0034026429542354133,4.5898157652229346
2026-04-14,49282,0.28973388671875,0.00054931640625,0.320892333984375,0.321441650390625,1977.2680053710938,17034.2975027528,5915929.666035999,11408211.587484161,1.691876669,11408213.279360830,1777.565031997,1597.3266997936526,65,362,0,16,861.8325517713765,0.8986038041033811,214183747.40069687,693470157.0487804,0.291656494140625,6850,9,18,14350,14447,66311.47207617608,59587.74106334696,0.0038015830672750496,0.0034161170058683594,4.5899821468938935
2026-04-13,45055,0.258880615234375,3.0517578125e-05,3.08563232421875,3.085662841796875,1970.029541015625,16962.452660004812,10602474.273976998,12624167.061212949,2.188581270,12624169.249794219,2504.906756893,2186.5560091132156,65,346,0,13,849.6913275652768,0.872909142464586,160236225.41463414,673504658.5017421,0.2611083984375,5698,10,16,13887,13990,64212.43973178697,56051.62570183307,0.0036968392444465888,0.0032270047746992994,4.589881324645245
2026-04-12,41393,0.25982666015625,0.0,3.71014404296875,3.71014404296875,1965.0768127441406,16911.509658647905,5254004.722119,9296796.503247193,1.443164622,9296797.946411815,3469.045848861,3011.2815287353656,65,623,0,0,839.7613681420703,0.8680431622787766,189386117.9512195,669538898.7735192,0.259429931640625,5639,7,16,14164,14260,65464.75831746463,56826.23582770784,0.0037802910168760395,0.0032814557686231295,4.5907965159512365
2026-04-11,41786,0.2708740234375,3.0517578125e-05,2.26739501953125,2.267425537109375,1969.6727905273438,16954.187906191888,5701138.53858,7323158.380762169,1.421976075,7323159.802738244,2893.330458415,2611.379936561755,65,624,0,0,839.1411738334067,0.9025515661257371,154128106.4703833,695983857.7909408,0.270843505859375,6105,7,15,14296,14403,66152.83255860217,59706.34262942003,0.0038104081365003812,0.00343908983117667,4.592989832576697
2026-04-10,63157,0.263671875,0.00018310546875,0.9664306640625,0.96661376953125,1974.984130859375,16997.612481599877,9776180.57874,11290432.002370237,2.356807469,11290434.359177706,2228.981786655,2021.4914787853327,65,702,0,0,839.0788317207681,0.9069125153413455,165317231.19512194,697813157.076655,0.2612438201904297,6200,7,15,14120,14218,65387.96950201947,59301.16789413967,0.0037567298957980233,0.0034070253592562165,4.59895692094665
2026-04-09,44696,0.29437255859375,0.0,0.72943115234375,0.72943115234375,1984.7205505371094,17056.66205241179,7942773.928979001,11659267.220217598,2.257414998,11659269.477632596,1945.885917653,1728.2416115592573,65,704,1,2,839.7533106639596,0.888151559082019,157767908.8466899,683318744.0034844,0.2939167022705078,6758,8,16,14131,14216,65433.63413296143,58114.984171592114,0.0037463387113268604,0.003327316567314273,4.602816132031615
2026-04-08,45610,0.230438232421875,0.0235595703125,0.821502685546875,0.845062255859375,1984.8153686523438,17053.22151479099,8779491.747283999,10187912.159084491,1.736075362,10187913.895159853,1906.328857312,1720.3044354154192,64,702,1,2,837.8562787016655,0.9024174547937743,257476681.32857144,694213177.0642858,0.228118896484375,6140,9,16,13956,14056,64706.30622777515,58392.1001751754,0.0037054436970020295,0.0033438570699302053,4.603465155647066
2026-04-07,43270,0.216644287109375,0.017059326171875,0.475128173828125,0.4921875,1987.9056701660156,17081.0580733658,7845375.569438,8421672.060161604,1.959910165,8421674.020071769,1803.447761567,1557.5893335219157,63,700,0,2,836.3538244238998,0.8636731080963166,221541228.85614035,664285828.1789473,0.21691894717514515,5860,9,16,14167,14265,65690.32406002822,56734.966352778814,0.003755663543460484,0.0032436656055445418,4.60499993410643
```
