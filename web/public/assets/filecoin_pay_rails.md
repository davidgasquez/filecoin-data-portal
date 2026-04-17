# main.filecoin_pay_rails

Published Filecoin Pay rails.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/filecoin_pay/rails.sql`
- dataset url: `https://data.filecoindataportal.xyz/filecoin_pay_rails.parquet`
- rows: `1323`

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
1322,0x305025d07c1dee47f25a4990179eff2becddca0b,0x40dbb5c4dc728b9d5f23444a1e5449d655ce0224,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5932568,17,0x0d20ddf9d055cac27e05fcab84ffe7e9f75c10f9a3986cfcbbd8c0a0eea2fa63,2026-04-15 20:04:00+00:00,null,null,null,null,null,null,null,False
1323,0x305025d07c1dee47f25a4990179eff2becddca0b,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5932568,20,0x0d20ddf9d055cac27e05fcab84ffe7e9f75c10f9a3986cfcbbd8c0a0eea2fa63,2026-04-15 20:04:00+00:00,5932568,24,0x0d20ddf9d055cac27e05fcab84ffe7e9f75c10f9a3986cfcbbd8c0a0eea2fa63,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5932568,2026-04-15 20:04:00+00:00,2026-04-15 20:04:00+00:00,True
1320,0x305025d07c1dee47f25a4990179eff2becddca0b,0x40dbb5c4dc728b9d5f23444a1e5449d655ce0224,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5932088,0,0x21b91cf3e003e188c83f62bc2e10ad4d19e553471c295bca7e55a068771169f3,2026-04-15 16:04:00+00:00,null,null,null,null,null,null,null,False
1321,0x305025d07c1dee47f25a4990179eff2becddca0b,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5932088,3,0x21b91cf3e003e188c83f62bc2e10ad4d19e553471c295bca7e55a068771169f3,2026-04-15 16:04:00+00:00,5932088,7,0x21b91cf3e003e188c83f62bc2e10ad4d19e553471c295bca7e55a068771169f3,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5932088,2026-04-15 16:04:00+00:00,2026-04-15 16:04:00+00:00,True
1318,0x4714c4f258978d9a261be4994da5431a5e483e4d,0x010ecc2436e0c5ea4741cd25a27a5476fe7a252c,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5931992,18,0xca071870cdb65bff423b79283d7c29127bafb92511a85a270833a274bbe00b54,2026-04-15 15:16:00+00:00,null,null,null,null,null,null,null,False
1319,0x4714c4f258978d9a261be4994da5431a5e483e4d,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5931992,20,0xca071870cdb65bff423b79283d7c29127bafb92511a85a270833a274bbe00b54,2026-04-15 15:16:00+00:00,5931992,24,0xca071870cdb65bff423b79283d7c29127bafb92511a85a270833a274bbe00b54,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5931992,2026-04-15 15:16:00+00:00,2026-04-15 15:16:00+00:00,True
1316,0x4714c4f258978d9a261be4994da5431a5e483e4d,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5931992,3,0xc17ea3e3ac996c1b999c933818557e5b38a08935c21f3491ae7476cd455eabab,2026-04-15 15:16:00+00:00,null,null,null,null,null,null,null,False
1317,0x4714c4f258978d9a261be4994da5431a5e483e4d,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5931992,6,0xc17ea3e3ac996c1b999c933818557e5b38a08935c21f3491ae7476cd455eabab,2026-04-15 15:16:00+00:00,5931992,10,0xc17ea3e3ac996c1b999c933818557e5b38a08935c21f3491ae7476cd455eabab,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5931992,2026-04-15 15:16:00+00:00,2026-04-15 15:16:00+00:00,True
1314,0x305025d07c1dee47f25a4990179eff2becddca0b,0x40dbb5c4dc728b9d5f23444a1e5449d655ce0224,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5931608,10,0x54b9c862becba3611036783c3ee9844b88ba1a7b9f6ba0500d597c89d658c9b2,2026-04-15 12:04:00+00:00,null,null,null,null,null,null,null,False
1315,0x305025d07c1dee47f25a4990179eff2becddca0b,0x23b1e018f08bb982348b15a86ee926eebf7f4daa,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x0000000000000000000000000000000000000000,0,True,5931608,13,0x54b9c862becba3611036783c3ee9844b88ba1a7b9f6ba0500d597c89d658c9b2,2026-04-15 12:04:00+00:00,5931608,17,0x54b9c862becba3611036783c3ee9844b88ba1a7b9f6ba0500d597c89d658c9b2,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5931608,2026-04-15 12:04:00+00:00,2026-04-15 12:04:00+00:00,True
```
