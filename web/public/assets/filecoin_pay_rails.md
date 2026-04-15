# main.filecoin_pay_rails

Published Filecoin Pay rails.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/filecoin_pay/rails.sql`
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
| `created_date` | `DATE` | UTC creation date. |  |
| `terminated_block` | `BIGINT` | Termination block number, if any. |  |
| `terminated_log_index` | `BIGINT` | Termination log index, if any. |  |
| `terminated_transaction_hash` | `VARCHAR` | Termination transaction hash, if any. |  |
| `terminated_by` | `VARCHAR` | Address that terminated the rail, if any. |  |
| `terminated_end_epoch` | `BIGINT` | End epoch emitted on termination, if any. |  |
| `terminated_date` | `DATE` | UTC termination date, if any. |  |
| `terminated_end_date` | `DATE` | UTC termination end date, if any. |  |
| `is_terminated` | `BOOLEAN` | Whether the rail has a termination event. |  |

## Sample (10 rows)

```csv
rail_id,payer,payee,token,operator,service,validator,service_fee_recipient,commission_rate_bps,is_arr_eligible,created_block,created_log_index,created_transaction_hash,created_date,terminated_block,terminated_log_index,terminated_transaction_hash,terminated_by,terminated_end_epoch,terminated_date,terminated_end_date,is_terminated
53,0xbbbdedc4fd24071d08a15d5b438e10d565d88003,0x89b5899619d93a180d38011b8aec849deea3f573,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5491219,130,0xd2e1df7a1de05e04259f8d19e26714872f29f80077c5a3f6d9a3eaee5c1a7105,2025-11-13,5812276,27,0xe4621ec7bb69d22ce4b39e0d7c50a6759495ff4fc78fdd7ba5cbf4b32f2e8870,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5898676,2026-03-05,2026-04-04,True
271,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,0x010ecc2436e0c5ea4741cd25a27a5476fe7a252c,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,False,5670001,266,0xca3d954df7fe245892cf58acd10281a02f42137eab791b41ebcca080fa593051,2026-01-14,5692910,61,0x38c5677b34677d2df195438d1f8c785fbe9644048c458bc584072aef005792ea,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5779310,2026-01-22,2026-02-21,True
281,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,False,5671323,211,0x2f7c9ba4068d5d3858194668accb2bde4961baa47909c094fa80cbb3579e016a,2026-01-15,5919382,22,0xfdd40215ed06beb0c291a1d722b69793d208b10ca41ea1097c46033f778131a1,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5995118,2026-04-11,2026-05-07,True
333,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,0x010ecc2436e0c5ea4741cd25a27a5476fe7a252c,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,False,5707321,35,0x15e513a3dc8925ec0844c58f315bc504ff6414e9322bdab29211c5c6b52ac8b0,2026-01-27,5919387,9,0x0a36218d39ac6d4ec1e9c653ec2394fab976424b7eef692d5b66487cffca51d0,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5995118,2026-04-11,2026-05-07,True
349,0x80cbbbed05396bfa69bc43cb97655ab7ec18c0aa,0x1d60d2f5960af6341e842c539985fa297e10d6ea,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5722029,34,0xce22b3ad9f73edcd087c5e31803f1bcedf1a8cd4b37a622dd77319439b418b43,2026-02-01,5839145,62,0x3add02d79fa2a2dd185adee7d02d0d9e4b110a863e9b7c591a32fae4c567c903,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5818130,2026-03-14,2026-03-07,True
389,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,0x846e8cad00fad118604623a283fc472d902b89c2,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,False,5808961,40,0x8038883549e243eeb8f507976d1eebe7e7a6e9f671bc5f18bd77b6e32359895f,2026-03-03,5919390,32,0xf7d60a468ddeba5d11f6f087250179b0b39e334ae33fef7fc69eacde7a61cca2,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5995118,2026-04-11,2026-05-07,True
421,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,0xb8f10da7a39aa54d696246c8e68a1a4aa123a5cd,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,False,5808967,48,0x98182bd2ca16d77a2b832bc6443e2ce9fb2e58b997c1852fd116f1f5384d8cd4,2026-03-03,5926116,24,0x39bd16edc1ee41b9f93ab6189882fc086ca6266b0d8252b55f50980441873304,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5999583,2026-04-13,2026-05-09,True
437,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,0x1674f650feb5b696f30e1bb920626c15bc62af30,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,False,5808970,35,0x90f648ce71d082a6f2e46069dcb933cafd351b739733fed77032c0dfa377ee4e,2026-03-03,5926125,4,0xc99889842917e3c7decd55087542790526310b43ca92cbb0b7255933963bb6bb,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5999584,2026-04-13,2026-05-09,True
446,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,0xafd1f948e8aef14c0b39058aa2fcff4ecb7c585d,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,False,5809083,45,0x0d4ead66eaf6ae87fe7b01f809a8c4c23013d51d829848659d25842597c4fe93,2026-03-04,5926127,35,0xda6069d00dc069896ae8604291083d8ff6834f7a9ce444e6041400eaf73106a8,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5999584,2026-04-13,2026-05-09,True
456,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,0x846e8cad00fad118604623a283fc472d902b89c2,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,False,5809085,9,0x1ae45259d77701c5f208f80df3513891dc2ff2f3ed279e17313e3bd70256c7a9,2026-03-04,5926129,16,0x8c82e874d23a84257070cfffc228fa58378e13d1fefddcd873c9892be921eb90,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5999584,2026-04-13,2026-05-09,True
```
