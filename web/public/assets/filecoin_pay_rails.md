# main.filecoin_pay_rails

Published Filecoin Pay rails.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/filecoin_pay/rails.sql`
- dataset url: `https://data.filecoindataportal.xyz/filecoin_pay_rails.parquet`
- rows: `1307`

## Depends

- `model.filecoin_pay_rails`

## Tests

- none

## Columns

| column | type | description | tests |
|---|---|---|---|
| `rail_id` | `BIGINT` | Filecoin Pay rail identifier. |  |
| `payer` | `VARCHAR` | Payer address. |  |
| `payee` | `VARCHAR` | Payee address. |  |
| `token` | `VARCHAR` | ERC20 token address. |  |
| `operator` | `VARCHAR` | Operator address. |  |
| `service` | `VARCHAR` | Service classification. |  |
| `validator` | `VARCHAR` | Validator address. |  |
| `service_fee_recipient` | `VARCHAR` | Service fee recipient address. |  |
| `commission_rate_bps` | `BIGINT` | Commission rate in basis points. |  |
| `is_arr_eligible` | `BOOLEAN` | Whether the rail counts toward ARR. |  |
| `created_block` | `BIGINT` | Creation block number. |  |
| `created_log_index` | `BIGINT` | Creation log index. |  |
| `created_transaction_hash` | `VARCHAR` | Creation transaction hash. |  |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | UTC creation timestamp. |  |
| `terminated_block` | `BIGINT` | Termination block number, if any. |  |
| `terminated_log_index` | `BIGINT` | Termination log index, if any. |  |
| `terminated_transaction_hash` | `VARCHAR` | Termination transaction hash, if any. |  |
| `terminated_by` | `VARCHAR` | Address that terminated the rail, if any. |  |
| `terminated_end_epoch` | `BIGINT` | End epoch emitted on termination, if any. |  |
| `terminated_at` | `TIMESTAMP WITH TIME ZONE` | UTC termination timestamp, if any. |  |
| `terminated_end_at` | `TIMESTAMP WITH TIME ZONE` | UTC termination end timestamp, if any. |  |
| `is_terminated` | `BOOLEAN` | Whether the rail has a termination event. |  |

## Sample (10 rows)

```csv
rail_id,payer,payee,token,operator,service,validator,service_fee_recipient,commission_rate_bps,is_arr_eligible,created_block,created_log_index,created_transaction_hash,created_at,terminated_block,terminated_log_index,terminated_transaction_hash,terminated_by,terminated_end_epoch,terminated_at,terminated_end_at,is_terminated
1307,0x305025d07c1dee47f25a4990179eff2becddca0b,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5929688,18,0x5c247161a179c2bf0778265010cc039652bccd0bb66439e2d6fa7f4d5127873e,2026-04-14 22:04:00+02:00,5929688,22,0x5c247161a179c2bf0778265010cc039652bccd0bb66439e2d6fa7f4d5127873e,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5929688,2026-04-14 22:04:00+02:00,2026-04-14 22:04:00+02:00,True
1306,0x305025d07c1dee47f25a4990179eff2becddca0b,0x40dbb5c4dc728b9d5f23444a1e5449d655ce0224,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5929688,15,0x5c247161a179c2bf0778265010cc039652bccd0bb66439e2d6fa7f4d5127873e,2026-04-14 22:04:00+02:00,null,null,null,null,null,null,null,False
1301,0x305025d07c1dee47f25a4990179eff2becddca0b,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5929208,10,0xcfa6575c6caf95368e560bb214abfee81da713bf0cbd48ed42dfe33feaf810e3,2026-04-14 18:04:00+02:00,5929208,14,0xcfa6575c6caf95368e560bb214abfee81da713bf0cbd48ed42dfe33feaf810e3,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5929208,2026-04-14 18:04:00+02:00,2026-04-14 18:04:00+02:00,True
1302,0x305025d07c1dee47f25a4990179eff2becddca0b,0xe2730269ef3bfcbc081a8d028e5c31d9a308a802,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5929208,22,0x776136866280e2e8f91bc98675d53c32c7436a1d6af7050f2b31ff1e9c84e6db,2026-04-14 18:04:00+02:00,null,null,null,null,null,null,null,False
1305,0x305025d07c1dee47f25a4990179eff2becddca0b,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5929208,38,0xf1e189cc72df4d95a699f8903679f11a05d9f87329272750344dfa63fe5bc163,2026-04-14 18:04:00+02:00,5929208,42,0xf1e189cc72df4d95a699f8903679f11a05d9f87329272750344dfa63fe5bc163,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5929208,2026-04-14 18:04:00+02:00,2026-04-14 18:04:00+02:00,True
1300,0x305025d07c1dee47f25a4990179eff2becddca0b,0x40dbb5c4dc728b9d5f23444a1e5449d655ce0224,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5929208,8,0xcfa6575c6caf95368e560bb214abfee81da713bf0cbd48ed42dfe33feaf810e3,2026-04-14 18:04:00+02:00,null,null,null,null,null,null,null,False
1303,0x305025d07c1dee47f25a4990179eff2becddca0b,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5929208,24,0x776136866280e2e8f91bc98675d53c32c7436a1d6af7050f2b31ff1e9c84e6db,2026-04-14 18:04:00+02:00,5929208,28,0x776136866280e2e8f91bc98675d53c32c7436a1d6af7050f2b31ff1e9c84e6db,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5929208,2026-04-14 18:04:00+02:00,2026-04-14 18:04:00+02:00,True
1304,0x305025d07c1dee47f25a4990179eff2becddca0b,0xb8f10da7a39aa54d696246c8e68a1a4aa123a5cd,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5929208,36,0xf1e189cc72df4d95a699f8903679f11a05d9f87329272750344dfa63fe5bc163,2026-04-14 18:04:00+02:00,null,null,null,null,null,null,null,False
1295,0x305025d07c1dee47f25a4990179eff2becddca0b,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5928728,12,0x9357bac4a7cabd6556cee9a189a0fbee37aa2b5f9ee21a3e8f7d61f148f60f3b,2026-04-14 14:04:00+02:00,5928728,16,0x9357bac4a7cabd6556cee9a189a0fbee37aa2b5f9ee21a3e8f7d61f148f60f3b,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5928728,2026-04-14 14:04:00+02:00,2026-04-14 14:04:00+02:00,True
1297,0x305025d07c1dee47f25a4990179eff2becddca0b,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5928728,26,0x0eb168fcb7e2bd829b40446e1babdd5200be7a6f98483dc2e643abcae430d105,2026-04-14 14:04:00+02:00,5928728,30,0x0eb168fcb7e2bd829b40446e1babdd5200be7a6f98483dc2e643abcae430d105,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5928728,2026-04-14 14:04:00+02:00,2026-04-14 14:04:00+02:00,True
```
