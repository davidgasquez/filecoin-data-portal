# main.foc_filecoin_pay_rail_rate_intervals

Mainnet Filecoin Pay rail rate intervals reconstructed from onchain events. Each row is a half-open interval [start_ordinal, end_ordinal) where a rail's recurring payment rate is constant.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/foc/filecoin_pay_rail_rate_intervals.sql`
- rows: `814909`

## Depends

- [`main.foc_filecoin_pay_rails`](foc_filecoin_pay_rails.md)
- `raw.fevm_eth_logs_decoded`

## Tests

- `not_null(rail_id)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `rail_id` | `BIGINT` | Filecoin Pay rail identifier. | `not_null` |
| `service` | `VARCHAR` | Service classification copied from main.foc_filecoin_pay_rails. |  |
| `payer` | `VARCHAR` | Payer address funding the rail. |  |
| `payee` | `VARCHAR` | Payee address receiving the rail payments. |  |
| `token` | `VARCHAR` | ERC20 token address used by the rail. |  |
| `operator` | `VARCHAR` | Operator address recorded on rail creation. |  |
| `validator` | `VARCHAR` | Validator address recorded on rail creation. |  |
| `is_arr_eligible` | `BOOLEAN` | Whether the rail should count toward USDFC ARR. |  |
| `start_block` | `BIGINT` | Inclusive block where the interval starts. |  |
| `start_log_index` | `BIGINT` | Inclusive log index where the interval starts. |  |
| `start_ordinal` | `BIGINT` | Inclusive event ordinal computed as block_number * 1000000 + log_index. |  |
| `start_date` | `DATE` | UTC date derived from the start block. |  |
| `end_block` | `BIGINT` | Exclusive block where the interval ends, if any. |  |
| `end_log_index` | `BIGINT` | Exclusive log index where the interval ends, if any. |  |
| `end_ordinal` | `BIGINT` | Exclusive event ordinal where the interval ends, if any. |  |
| `end_date` | `DATE` | UTC date derived from the end block, if any. |  |
| `rate_wei_per_epoch` | `BIGINT` | Constant recurring payment rate during the interval, in token wei per epoch. |  |
| `rate_token_per_epoch` | `DOUBLE` | Constant recurring payment rate during the interval, scaled to whole-token units. |  |

## Sample (10 rows)

```csv
rail_id,service,payer,payee,token,operator,validator,is_arr_eligible,start_block,start_log_index,start_ordinal,start_date,end_block,end_log_index,end_ordinal,end_date,rate_wei_per_epoch,rate_token_per_epoch
1,FWSS,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,True,5465826,32,5465826000032,2025-11-04,5465828,108,5465828000108,2025-11-04,0,0.0
1,FWSS,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,True,5465828,108,5465828000108,2025-11-04,5468717,33,5468717000033,2025-11-05,694444444444,6.94444444444e-07
1,FWSS,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,True,5468717,33,5468717000033,2025-11-05,5471589,147,5471589000147,2025-11-06,694444444444,6.94444444444e-07
1,FWSS,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,True,5471589,147,5471589000147,2025-11-06,5474469,39,5474469000039,2025-11-07,694444444444,6.94444444444e-07
1,FWSS,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,True,5474469,39,5474469000039,2025-11-07,5477349,50,5477349000050,2025-11-08,694444444444,6.94444444444e-07
1,FWSS,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,True,5477349,50,5477349000050,2025-11-08,5480229,24,5480229000024,2025-11-09,694444444444,6.94444444444e-07
1,FWSS,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,True,5480229,24,5480229000024,2025-11-09,5483109,38,5483109000038,2025-11-10,694444444444,6.94444444444e-07
1,FWSS,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,True,5483109,38,5483109000038,2025-11-10,5485989,1,5485989000001,2025-11-11,694444444444,6.94444444444e-07
1,FWSS,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,True,5485989,1,5485989000001,2025-11-11,5488868,180,5488868000180,2025-11-12,694444444444,6.94444444444e-07
1,FWSS,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,True,5488868,180,5488868000180,2025-11-12,5491749,131,5491749000131,2025-11-13,694444444444,6.94444444444e-07
```
