# main.filecoin_pay_rails

Published Filecoin Pay rails.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/filecoin_pay/rails.sql`
- dataset url: `https://data.filecoindataportal.xyz/filecoin_pay_rails.parquet`
- rows: `1332`

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
1331,0xf382e9425224c123746f7312fb0dbec81b51a10c,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5937739,72,0xe81a0b3a2dd1df4824cd9f9ac8f14a69912d8d7c0587d8d43eadfc133b3cf995,2026-04-17 15:09:30+00:00,null,null,null,null,null,null,null,False
1332,0xf382e9425224c123746f7312fb0dbec81b51a10c,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5937739,74,0xe81a0b3a2dd1df4824cd9f9ac8f14a69912d8d7c0587d8d43eadfc133b3cf995,2026-04-17 15:09:30+00:00,5937739,78,0xe81a0b3a2dd1df4824cd9f9ac8f14a69912d8d7c0587d8d43eadfc133b3cf995,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5937739,2026-04-17 15:09:30+00:00,2026-04-17 15:09:30+00:00,True
1330,0x1721eb5d0b038b07f356d7c3858e6f1fb10089ea,0x89b5899619d93a180d38011b8aec849deea3f573,0xeb466342c4d449bc9f53a865d5cb90586f405215,0x96f1a3026eac5a6c10cd121ef58d3c13d150e441,FWSS,0x96f1a3026eac5a6c10cd121ef58d3c13d150e441,0x0000000000000000000000000000000000000000,0,False,5934925,21,0x226ff7891ba46f89d38a586234947c87698681ad4c1b568cf15400581488ebbf,2026-04-16 15:42:30+00:00,null,null,null,null,null,null,null,False
1329,0x305025d07c1dee47f25a4990179eff2becddca0b,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5934008,8,0x1165dc46bf93fd3a582e5ef0b3b61ad43271fd1b201b664a0edbb9438819a30b,2026-04-16 08:04:00+00:00,5934008,12,0x1165dc46bf93fd3a582e5ef0b3b61ad43271fd1b201b664a0edbb9438819a30b,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5934008,2026-04-16 08:04:00+00:00,2026-04-16 08:04:00+00:00,True
1328,0x305025d07c1dee47f25a4990179eff2becddca0b,0x40dbb5c4dc728b9d5f23444a1e5449d655ce0224,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5934008,5,0x1165dc46bf93fd3a582e5ef0b3b61ad43271fd1b201b664a0edbb9438819a30b,2026-04-16 08:04:00+00:00,null,null,null,null,null,null,null,False
1327,0x305025d07c1dee47f25a4990179eff2becddca0b,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5933528,16,0x46fe6901b4c8b674efbce37e00c54b7d6a1c5a7ff7f0f459ad100f69fc7d6e0d,2026-04-16 04:04:00+00:00,5933528,20,0x46fe6901b4c8b674efbce37e00c54b7d6a1c5a7ff7f0f459ad100f69fc7d6e0d,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5933528,2026-04-16 04:04:00+00:00,2026-04-16 04:04:00+00:00,True
1326,0x305025d07c1dee47f25a4990179eff2becddca0b,0x40dbb5c4dc728b9d5f23444a1e5449d655ce0224,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5933528,13,0x46fe6901b4c8b674efbce37e00c54b7d6a1c5a7ff7f0f459ad100f69fc7d6e0d,2026-04-16 04:04:00+00:00,null,null,null,null,null,null,null,False
1324,0x305025d07c1dee47f25a4990179eff2becddca0b,0x40dbb5c4dc728b9d5f23444a1e5449d655ce0224,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5933048,0,0x48dabfc8abc8722d0f3da2bbdae00eb1f48a72f6d9231ced962477ed40463911,2026-04-16 00:04:00+00:00,null,null,null,null,null,null,null,False
1325,0x305025d07c1dee47f25a4990179eff2becddca0b,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5933048,3,0x48dabfc8abc8722d0f3da2bbdae00eb1f48a72f6d9231ced962477ed40463911,2026-04-16 00:04:00+00:00,5933048,7,0x48dabfc8abc8722d0f3da2bbdae00eb1f48a72f6d9231ced962477ed40463911,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5933048,2026-04-16 00:04:00+00:00,2026-04-16 00:04:00+00:00,True
1322,0x305025d07c1dee47f25a4990179eff2becddca0b,0x40dbb5c4dc728b9d5f23444a1e5449d655ce0224,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5932568,17,0x0d20ddf9d055cac27e05fcab84ffe7e9f75c10f9a3986cfcbbd8c0a0eea2fa63,2026-04-15 20:04:00+00:00,null,null,null,null,null,null,null,False
```
