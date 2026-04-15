# main.warm_storage_datasets

Published warm storage datasets.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/warm_storage/datasets.sql`
- rows: `834`

## Depends

- `model.warm_storage_datasets`

## Tests

- none

## Columns

| column | type | description | tests |
|---|---|---|---|
| `dataset_id` | `BIGINT` | FWSS dataset identifier. |  |
| `payer` | `VARCHAR` | Payer address. |  |
| `provider_id` | `BIGINT` | Service provider registry identifier. |  |
| `service_provider` | `VARCHAR` | Service provider address. |  |
| `payee` | `VARCHAR` | Payee address. |  |
| `pdp_rail_id` | `BIGINT` | Filecoin Pay PDP rail identifier. |  |
| `cache_miss_rail_id` | `BIGINT` | Filecoin Pay cache-miss rail identifier, if any. |  |
| `cdn_rail_id` | `BIGINT` | Filecoin Pay CDN rail identifier, if any. |  |
| `has_cdn` | `BOOLEAN` | Whether CDN payment rails were configured. |  |
| `created_block` | `BIGINT` | Creation block number. |  |
| `created_date` | `DATE` | UTC creation date. |  |
| `billing_started_block` | `BIGINT` | First block with a positive billing rate, if any. |  |
| `billing_started_date` | `DATE` | UTC billing start date, if any. |  |
| `billing_terminated_block` | `BIGINT` | Billing termination block, if any. |  |
| `billing_terminated_date` | `DATE` | UTC billing termination date, if any. |  |
| `settlement_end_epoch` | `BIGINT` | Settlement end epoch, if any. |  |
| `settlement_end_date` | `DATE` | UTC settlement end date, if any. |  |

## Sample (10 rows)

```csv
dataset_id,payer,provider_id,service_provider,payee,pdp_rail_id,cache_miss_rail_id,cdn_rail_id,has_cdn,created_block,created_date,billing_started_block,billing_started_date,billing_terminated_block,billing_terminated_date,settlement_end_epoch,settlement_end_date
50,0x2c67808c7a22639bfecff9d098e72a6b205f4809,7,0x89b5899619d93a180d38011b8aec849deea3f573,0x89b5899619d93a180d38011b8aec849deea3f573,62,null,null,False,5491219,2025-11-13,5491915,2025-11-13,5812274,2026-03-05,5898674,2026-04-04
130,0x3e4e5f067cfda2f16aade21912b8324c3d9624f8,5,0x010ecc2436e0c5ea4741cd25a27a5476fe7a252c,0x010ecc2436e0c5ea4741cd25a27a5476fe7a252c,168,169,170,True,5589783,2025-12-17,5589785,2025-12-17,5676212,2026-01-16,5762612,2026-02-15
200,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,280,281,282,True,5671323,2026-01-15,5671325,2026-01-15,5919382,2026-04-11,5995118,2026-05-07
246,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,3,0xafd1f948e8aef14c0b39058aa2fcff4ecb7c585d,0xafd1f948e8aef14c0b39058aa2fcff4ecb7c585d,346,null,null,False,5721961,2026-02-01,5721961,2026-02-01,5730759,2026-02-04,5817159,2026-03-06
319,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,16,0x1674f650feb5b696f30e1bb920626c15bc62af30,0x1674f650feb5b696f30e1bb920626c15bc62af30,425,null,null,False,5808968,2026-03-03,5809075,2026-03-03,5926116,2026-04-13,5999583,2026-05-09
336,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,442,null,null,False,5809083,2026-03-04,5809180,2026-03-04,5920124,2026-04-11,5995118,2026-05-07
357,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,3,0xafd1f948e8aef14c0b39058aa2fcff4ecb7c585d,0xafd1f948e8aef14c0b39058aa2fcff4ecb7c585d,463,null,null,False,5809087,2026-03-04,5809125,2026-03-04,5926131,2026-04-13,5999584,2026-05-09
375,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,2,0x86d026029052c6582d277d9b28700edc9670b150,0x86d026029052c6582d277d9b28700edc9670b150,481,null,null,False,5809203,2026-03-04,5809458,2026-03-04,5926135,2026-04-13,5999584,2026-05-09
391,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,16,0x1674f650feb5b696f30e1bb920626c15bc62af30,0x1674f650feb5b696f30e1bb920626c15bc62af30,497,null,null,False,5809207,2026-03-04,5809875,2026-03-04,5926137,2026-04-13,5999584,2026-05-09
410,0xa5f90bc2aa73a2e0bad4d7092a932644d5dd5d71,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,516,null,null,False,5809327,2026-03-04,5810891,2026-03-04,5926141,2026-04-13,5999584,2026-05-09
```
