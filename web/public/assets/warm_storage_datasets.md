# main.warm_storage_datasets

Published warm storage datasets.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/warm_storage/datasets.sql`
- dataset url: `https://data.filecoindataportal.xyz/warm_storage_datasets.parquet`
- rows: `842`

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
| `created_at` | `TIMESTAMP WITH TIME ZONE` | UTC creation timestamp. |  |
| `billing_started_block` | `BIGINT` | First block with a positive billing rate, if any. |  |
| `billing_started_at` | `TIMESTAMP WITH TIME ZONE` | UTC billing start timestamp, if any. |  |
| `billing_terminated_block` | `BIGINT` | Billing termination block, if any. |  |
| `billing_terminated_at` | `TIMESTAMP WITH TIME ZONE` | UTC billing termination timestamp, if any. |  |
| `settlement_end_epoch` | `BIGINT` | Settlement end epoch, if any. |  |
| `settlement_end_at` | `TIMESTAMP WITH TIME ZONE` | UTC settlement end timestamp, if any. |  |

## Sample (10 rows)

```csv
dataset_id,payer,provider_id,service_provider,payee,pdp_rail_id,cache_miss_rail_id,cdn_rail_id,has_cdn,created_block,created_at,billing_started_block,billing_started_at,billing_terminated_block,billing_terminated_at,settlement_end_epoch,settlement_end_at
1,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,1,null,null,False,5465826,2025-11-04 18:33:00+00:00,5465828,2025-11-04 18:34:00+00:00,null,null,null,null
2,0xaf992fbc0c22bc941a232c63dc1b0c0cd572d145,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,2,3,4,True,5467575,2025-11-05 09:07:30+00:00,5467577,2025-11-05 09:08:30+00:00,null,null,null,null
3,0xaf992fbc0c22bc941a232c63dc1b0c0cd572d145,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,5,null,null,False,5467591,2025-11-05 09:15:30+00:00,5467593,2025-11-05 09:16:30+00:00,null,null,null,null
4,0xaf992fbc0c22bc941a232c63dc1b0c0cd572d145,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,6,7,8,True,5467605,2025-11-05 09:22:30+00:00,5467607,2025-11-05 09:23:30+00:00,null,null,null,null
5,0x741c0a74b858396c966fb139db17e4ad484cc446,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,9,10,11,True,5471214,2025-11-06 15:27:00+00:00,5471217,2025-11-06 15:28:30+00:00,null,null,null,null
6,0x741c0a74b858396c966fb139db17e4ad484cc446,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,12,13,14,True,5471219,2025-11-06 15:29:30+00:00,5471221,2025-11-06 15:30:30+00:00,null,null,null,null
7,0x838294adde22f9dcc62a0e6ed99aaad4d037ca3a,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,15,null,null,False,5472377,2025-11-07 01:08:30+00:00,5472386,2025-11-07 01:13:00+00:00,5813543,2026-03-05 12:11:30+00:00,5567426,2025-12-10 01:13:00+00:00
8,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,16,null,null,False,5473782,2025-11-07 12:51:00+00:00,5473784,2025-11-07 12:52:00+00:00,null,null,null,null
9,0x7d3f0ca48194490d7c8b60fea6225e817ec52aa9,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,17,null,null,False,5474343,2025-11-07 17:31:30+00:00,5474360,2025-11-07 17:40:00+00:00,5813543,2026-03-05 12:11:30+00:00,5583800,2025-12-15 17:40:00+00:00
10,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,5,0x010ecc2436e0c5ea4741cd25a27a5476fe7a252c,0x010ecc2436e0c5ea4741cd25a27a5476fe7a252c,18,null,null,False,5485045,2025-11-11 10:42:30+00:00,5485047,2025-11-11 10:43:30+00:00,null,null,null,null
```
