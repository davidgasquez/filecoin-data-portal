# main.foc_filecoin_warm_storage_datasets

Mainnet Filecoin Warm Storage Service datasets created onchain. Includes dataset parties, payment rail identifiers, and billing lifecycle derived from FWSS events.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/foc/filecoin_warm_storage_datasets.sql`
- rows: `834`

## Depends

- `raw.fevm_eth_logs_decoded`

## Tests

- `not_null(data_set_id)`
- `unique(data_set_id)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `data_set_id` | `BIGINT` | FWSS data set identifier. | `not_null`, `unique` |
| `payer` | `VARCHAR` | Payer address funding the dataset on mainnet. |  |
| `provider_id` | `BIGINT` | Service provider registry identifier selected for the dataset. |  |
| `service_provider` | `VARCHAR` | Service provider address recorded by FWSS. |  |
| `payee` | `VARCHAR` | Payee address recorded by FWSS for the dataset. |  |
| `pdp_rail_id` | `BIGINT` | Filecoin Pay PDP rail identifier for the dataset. |  |
| `cache_miss_rail_id` | `BIGINT` | Filecoin Pay cache-miss rail identifier for the dataset, if CDN is enabled. |  |
| `cdn_rail_id` | `BIGINT` | Filecoin Pay CDN rail identifier for the dataset, if CDN is enabled. |  |
| `has_cdn` | `BOOLEAN` | Whether the dataset was created with CDN payment rails. |  |
| `created_block` | `BIGINT` | Block when the dataset was created in FWSS. |  |
| `created_date` | `DATE` | UTC date of dataset creation derived from the creation block. |  |
| `billing_started_block` | `BIGINT` | First block where FWSS emitted a positive RailRateUpdated for the dataset. |  |
| `billing_started_date` | `DATE` | UTC date when the dataset first became chargeable. |  |
| `billing_terminated_block` | `BIGINT` | Block where FWSS emitted PDPPaymentTerminated for the dataset, if any. |  |
| `billing_terminated_date` | `DATE` | UTC date when the PDP billing rail was terminated, if any. |  |
| `settlement_end_epoch` | `BIGINT` | Final settlement epoch emitted with PDPPaymentTerminated, if any. |  |
| `settlement_end_date` | `DATE` | UTC date derived from settlement_end_epoch, if any. |  |

## Sample (10 rows)

```csv
data_set_id,payer,provider_id,service_provider,payee,pdp_rail_id,cache_miss_rail_id,cdn_rail_id,has_cdn,created_block,created_date,billing_started_block,billing_started_date,billing_terminated_block,billing_terminated_date,settlement_end_epoch,settlement_end_date
1,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,1,null,null,False,5465826,2025-11-04,5465828,2025-11-04,null,null,null,null
2,0xaf992fbc0c22bc941a232c63dc1b0c0cd572d145,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,2,3,4,True,5467575,2025-11-05,5467577,2025-11-05,null,null,null,null
3,0xaf992fbc0c22bc941a232c63dc1b0c0cd572d145,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,5,null,null,False,5467591,2025-11-05,5467593,2025-11-05,null,null,null,null
4,0xaf992fbc0c22bc941a232c63dc1b0c0cd572d145,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,6,7,8,True,5467605,2025-11-05,5467607,2025-11-05,null,null,null,null
5,0x741c0a74b858396c966fb139db17e4ad484cc446,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,9,10,11,True,5471214,2025-11-06,5471217,2025-11-06,null,null,null,null
6,0x741c0a74b858396c966fb139db17e4ad484cc446,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,12,13,14,True,5471219,2025-11-06,5471221,2025-11-06,null,null,null,null
7,0x838294adde22f9dcc62a0e6ed99aaad4d037ca3a,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,15,null,null,False,5472377,2025-11-07,5472386,2025-11-07,5813543,2026-03-05,5567426,2025-12-10
8,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,16,null,null,False,5473782,2025-11-07,5473784,2025-11-07,null,null,null,null
9,0x7d3f0ca48194490d7c8b60fea6225e817ec52aa9,1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,17,null,null,False,5474343,2025-11-07,5474360,2025-11-07,5813543,2026-03-05,5583800,2025-12-15
10,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,5,0x010ecc2436e0c5ea4741cd25a27a5476fe7a252c,0x010ecc2436e0c5ea4741cd25a27a5476fe7a252c,18,null,null,False,5485045,2025-11-11,5485047,2025-11-11,null,null,null,null
```
