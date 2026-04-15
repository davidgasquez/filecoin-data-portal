# main.foc_filecoin_pay_rails

Mainnet Filecoin Pay rails reconstructed from onchain events. Includes creation and termination lifecycle, ARR eligibility, and service classification.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/foc/filecoin_pay_rails.sql`
- rows: `1307`

## Depends

- `raw.fevm_eth_logs_decoded`

## Tests

- `not_null(rail_id)`
- `unique(rail_id)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `rail_id` | `BIGINT` | Filecoin Pay rail identifier. | `not_null`, `unique` |
| `payer` | `VARCHAR` | Payer address funding the rail. |  |
| `payee` | `VARCHAR` | Payee address receiving the rail payments. |  |
| `token` | `VARCHAR` | ERC20 token address used by the rail. |  |
| `operator` | `VARCHAR` | Operator address recorded on rail creation. |  |
| `service` | `VARCHAR` | Service classification derived from operator: Storacha for the Storacha operator address, otherwise FWSS. |  |
| `validator` | `VARCHAR` | Validator address recorded on rail creation. |  |
| `service_fee_recipient` | `VARCHAR` | Service fee recipient address recorded on rail creation. |  |
| `commission_rate_bps` | `BIGINT` | Commission rate in basis points recorded on rail creation. |  |
| `is_arr_eligible` | `BOOLEAN` | Whether the rail should count toward USDFC ARR (USDFC token and non-DealBot payer). |  |
| `created_block` | `BIGINT` | Block where the rail was created. |  |
| `created_log_index` | `BIGINT` | Log index of the RailCreated event. |  |
| `created_transaction_hash` | `VARCHAR` | Transaction hash of the RailCreated event. |  |
| `created_date` | `DATE` | UTC date derived from the creation block. |  |
| `terminated_block` | `BIGINT` | Block where the rail was terminated, if any. |  |
| `terminated_log_index` | `BIGINT` | Log index of the RailTerminated event, if any. |  |
| `terminated_transaction_hash` | `VARCHAR` | Transaction hash of the RailTerminated event, if any. |  |
| `terminated_by` | `VARCHAR` | Address that terminated the rail, if any. |  |
| `terminated_end_epoch` | `BIGINT` | End epoch emitted by RailTerminated, if any. |  |
| `terminated_date` | `DATE` | UTC date derived from the termination block, if any. |  |
| `terminated_end_date` | `DATE` | UTC date derived from the termination end epoch, if any. |  |
| `is_terminated` | `BOOLEAN` | Whether the rail has a termination event. |  |

## Sample (10 rows)

```csv
rail_id,payer,payee,token,operator,service,validator,service_fee_recipient,commission_rate_bps,is_arr_eligible,created_block,created_log_index,created_transaction_hash,created_date,terminated_block,terminated_log_index,terminated_transaction_hash,terminated_by,terminated_end_epoch,terminated_date,terminated_end_date,is_terminated
1,0x2127c3a31f54b81b5e9ad1e29c36c420d3d6ecc5,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5465826,32,0x0f47eaa739dabe14b0d6a2eefd5fbebf0df7ac056f1e36f4cfd08d0f9dbb09bc,2025-11-04,null,null,null,null,null,null,null,False
2,0xaf992fbc0c22bc941a232c63dc1b0c0cd572d145,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5467575,7,0x5b274ed43b10ec01eb5847c5c62ed1651a0dc735768a22d5f481f5822c2f831f,2025-11-05,null,null,null,null,null,null,null,False
3,0xaf992fbc0c22bc941a232c63dc1b0c0cd572d145,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5467575,10,0x5b274ed43b10ec01eb5847c5c62ed1651a0dc735768a22d5f481f5822c2f831f,2025-11-05,null,null,null,null,null,null,null,False
4,0xaf992fbc0c22bc941a232c63dc1b0c0cd572d145,0x1d60d2f5960af6341e842c539985fa297e10d6ea,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5467575,12,0x5b274ed43b10ec01eb5847c5c62ed1651a0dc735768a22d5f481f5822c2f831f,2025-11-05,null,null,null,null,null,null,null,False
5,0xaf992fbc0c22bc941a232c63dc1b0c0cd572d145,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5467591,167,0x00043d97f93a1b739cfdcc41df71e43908f18fe24520ac5dd5ca178e0e9c86e4,2025-11-05,null,null,null,null,null,null,null,False
6,0xaf992fbc0c22bc941a232c63dc1b0c0cd572d145,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5467605,51,0x513c538cedf354b0e90263060a04eb1ff3a04abe68c7cf88bdd8551cce6b86a3,2025-11-05,null,null,null,null,null,null,null,False
7,0xaf992fbc0c22bc941a232c63dc1b0c0cd572d145,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5467605,54,0x513c538cedf354b0e90263060a04eb1ff3a04abe68c7cf88bdd8551cce6b86a3,2025-11-05,null,null,null,null,null,null,null,False
8,0xaf992fbc0c22bc941a232c63dc1b0c0cd572d145,0x1d60d2f5960af6341e842c539985fa297e10d6ea,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5467605,56,0x513c538cedf354b0e90263060a04eb1ff3a04abe68c7cf88bdd8551cce6b86a3,2025-11-05,null,null,null,null,null,null,null,False
9,0x741c0a74b858396c966fb139db17e4ad484cc446,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5471214,126,0x7df7e50ef452205649439cf4dc3416c2187443958b4e374619e38c81c355b212,2025-11-06,null,null,null,null,null,null,null,False
10,0x741c0a74b858396c966fb139db17e4ad484cc446,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x80b98d3aa09ffff255c3ba4a241111ff1262f045,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,FWSS,0x0000000000000000000000000000000000000000,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,0,True,5471214,129,0x7df7e50ef452205649439cf4dc3416c2187443958b4e374619e38c81c355b212,2025-11-06,5471224,99,0xf9a6821c6fc999c4fca1b9201e3aac252f5b27a17a5e06d72f16fc7cda257985,0x8408502033c418e1bbc97ce9ac48e5528f371a9f,5557624,2025-11-06,2025-12-06,True
```
