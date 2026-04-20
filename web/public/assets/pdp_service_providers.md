# main.pdp_service_providers

Published PDP service providers.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/pdp/service_providers.sql`
- dataset url: `https://data.filecoindataportal.xyz/pdp_service_providers.parquet`
- rows: `27`

## Depends

- `raw.fevm_eth_logs_decoded`

## Tests

- `not_null(provider_id)`
- `unique(provider_id)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `provider_id` | `BIGINT` | Service provider registry identifier. | `not_null`, `unique` |
| `service_provider` | `VARCHAR` | Provider control address. |  |
| `payee` | `VARCHAR` | Payee address. |  |
| `is_registered` | `BOOLEAN` | Whether the provider has a registration event. |  |
| `is_removed` | `BOOLEAN` | Whether the provider has a removal event. |  |
| `is_active` | `BOOLEAN` | Whether the provider is active based on registry and PDP product state. |  |
| `product_type` | `VARCHAR` | Latest PDP product type label. |  |
| `offers_pdp_storage` | `BOOLEAN` | Whether the latest PDP product event indicates an active PDP offering. |  |
| `service_url` | `VARCHAR` | Service endpoint URL decoded from capabilities. |  |
| `location` | `VARCHAR` | Provider location decoded from capabilities. |  |
| `location_country_code` | `VARCHAR` | Country code parsed from the location DN. |  |
| `location_region` | `VARCHAR` | State or region parsed from the location DN. |  |
| `location_city` | `VARCHAR` | City parsed from the location DN. |  |
| `payment_token_address` | `VARCHAR` | Payment token address from capabilities. |  |
| `min_piece_size_bytes` | `BIGINT` | Minimum supported piece size, in bytes. |  |
| `max_piece_size_bytes` | `BIGINT` | Maximum supported piece size, in bytes. |  |
| `storage_price_per_tib_per_day` | `BIGINT` | Storage price per TiB per day in token base units. |  |
| `min_proving_period_epochs` | `BIGINT` | Minimum proving period, in epochs. |  |
| `supports_ipni_piece` | `BOOLEAN` | Whether IPNI piece support is declared. |  |
| `supports_ipni_ipfs` | `BOOLEAN` | Whether IPNI IPFS support is declared. |  |
| `ipni_peer_id_hex` | `VARCHAR` | Raw hex-encoded IPNI peer id. |  |
| `capacity_tib_text` | `VARCHAR` | Capacity text from extra capabilities, if any. |  |
| `capacity_tib` | `DOUBLE` | Parsed numeric capacity, in TiB, if any. |  |
| `service_status` | `VARCHAR` | Service status from extra capabilities, if any. |  |
| `capabilities_json` | `JSON` | Latest active PDP capability key-value pairs. |  |
| `registered_block` | `BIGINT` | Registration block number. |  |
| `registered_transaction_hash` | `VARCHAR` | Registration transaction hash. |  |
| `registered_at` | `TIMESTAMP WITH TIME ZONE` | UTC registration timestamp. |  |
| `product_updated_block` | `BIGINT` | Latest PDP product lifecycle block. |  |
| `product_updated_transaction_hash` | `VARCHAR` | Latest PDP product lifecycle transaction hash. |  |
| `product_updated_at` | `TIMESTAMP WITH TIME ZONE` | UTC latest PDP product lifecycle timestamp. |  |
| `is_fwss_approved` | `BOOLEAN` | Whether the latest FWSS approval event is approved. |  |
| `fwss_first_approved_block` | `BIGINT` | First FWSS approval block, if any. |  |
| `fwss_first_approved_at` | `TIMESTAMP WITH TIME ZONE` | UTC first FWSS approval timestamp, if any. |  |
| `fwss_last_approval_block` | `BIGINT` | Latest FWSS approval block, if any. |  |
| `fwss_last_approval_transaction_hash` | `VARCHAR` | Latest FWSS approval transaction hash, if any. |  |
| `fwss_last_approval_at` | `TIMESTAMP WITH TIME ZONE` | UTC latest FWSS approval timestamp, if any. |  |

## Sample (10 rows)

```csv
provider_id,service_provider,payee,is_registered,is_removed,is_active,product_type,offers_pdp_storage,service_url,location,location_country_code,location_region,location_city,payment_token_address,min_piece_size_bytes,max_piece_size_bytes,storage_price_per_tib_per_day,min_proving_period_epochs,supports_ipni_piece,supports_ipni_ipfs,ipni_peer_id_hex,capacity_tib_text,capacity_tib,service_status,capabilities_json,registered_block,registered_transaction_hash,registered_at,product_updated_block,product_updated_transaction_hash,product_updated_at,is_fwss_approved,fwss_first_approved_block,fwss_first_approved_at,fwss_last_approval_block,fwss_last_approval_transaction_hash,fwss_last_approval_at
18,0x4de3d41c4fc6a80c9a5c908f3c6f4e48975637fd,0x4de3d41c4fc6a80c9a5c908f3c6f4e48975637fd,True,False,True,PDP,True,https://storacha.network,earth,null,null,null,0x4de3d41c4fc6a80c9a5c908f3c6f4e48975637fd,1,1,1,1,null,null,null,null,null,null,"{""paymentTokenAddress"":""0x4de3d41c4fc6a80c9a5c908f3c6f4e48975637fd"",""location"":""0x6561727468"",""minProvingPeriodInEpochs"":""0x01"",""storagePricePerTibPerDay"":""0x01"",""maxPieceSizeInBytes"":""0x01"",""minPieceSizeInBytes"":""0x01"",""serviceURL"":""0x68747470733a2f2f73746f72616368612e6e6574776f726b""}",5535714,0x5327e820ed39045e15c47fc11903e69b7da122aae06cfe0e968f8842aaada2c6,2025-11-29 00:57:00+00:00,5535714,0x5327e820ed39045e15c47fc11903e69b7da122aae06cfe0e968f8842aaada2c6,2025-11-29 00:57:00+00:00,False,null,null,null,null,null
10,0x74075b4a9e00304c2dddbae4a76399830c917544,0x74075b4a9e00304c2dddbae4a76399830c917544,True,False,True,PDP,True,https://mokanla.meje.dev,C=NG;ST=Lagos;L=Lagos,NG,Lagos,Lagos,0x0000000000000000000000000000000000000000,1048576,1073741824,83333333333333330,30,True,True,0x00240801122024a43e835a090adfcdcb65b95c6f934a345e4e206562f66888faeccc1ae98111,1,1.0,testing,"{""capacityTib"":""0x31"",""serviceStatus"":""0x74657374696e67"",""IPNIPeerID"":""0x00240801122024a43e835a090adfcdcb65b95c6f934a345e4e206562f66888faeccc1ae98111"",""ipniIpfs"":""0x01"",""ipniPiece"":""0x01"",""paymentTokenAddress"":""0x0000000000000000000000000000000000000000"",""location"":""0x433d4e473b53543d4c61676f733b4c3d4c61676f73"",""minProvingPeriodInEpochs"":""0x1e"",""storagePricePerTibPerDay"":""0x01280f39a3485552"",""maxPieceSizeInBytes"":""0x40000000"",""minPieceSizeInBytes"":""0x100000"",""serviceURL"":""0x68747470733a2f2f6d6f6b616e6c612e6d656a652e646576""}",5488948,0x133bec4c34cd4566d5771fd25770e311ec5ab325ead44842026558828e37150a,2025-11-12 19:14:00+00:00,5724256,0x92b0a31ad528d5ca5078c4eaf64a8e92440e7ceea67eaba4bc5e24d914e9f494,2026-02-02 12:08:00+00:00,False,null,null,null,null,null
2,0x86d026029052c6582d277d9b28700edc9670b150,0x86d026029052c6582d277d9b28700edc9670b150,True,False,True,PDP,True,https://pdp-main.660688.xyz:8443,C=CN;ST=Zhejiang;L=Hangzhou,CN,Zhejiang,Hangzhou,0x0000000000000000000000000000000000000000,1048576,1073741824,83333333333333330,30,True,True,0x002408011220b45c4247d808f10ebfa3532764d0dd5893524bc91108c8486ba7b9b9195eee8c,12,12.0,prod,"{""capacityTib"":""0x3132"",""serviceStatus"":""0x70726f64"",""IPNIPeerID"":""0x002408011220b45c4247d808f10ebfa3532764d0dd5893524bc91108c8486ba7b9b9195eee8c"",""ipniPeerId"":""0x002408011220b45c4247d808f10ebfa3532764d0dd5893524bc91108c8486ba7b9b9195eee8c"",""ipniIpfs"":""0x01"",""ipniPiece"":""0x01"",""paymentTokenAddress"":""0x0000000000000000000000000000000000000000"",""location"":""0x433d434e3b53543d5a68656a69616e673b4c3d48616e677a686f75"",""minProvingPeriodInEpochs"":""0x1e"",""storagePricePerTibPerDay"":""0x01280f39a3485552"",""maxPieceSizeInBytes"":""0x40000000"",""minPieceSizeInBytes"":""0x100000"",""serviceURL"":""0x68747470733a2f2f7064702d6d61696e2e3636303638382e78797a3a38343433""}",5476431,0xe4e00123e5b0c83a1272ad9358108adb614b1c0c1706f394e080ca0671424f81,2025-11-08 10:55:30+00:00,5874396,0x49bcc4b898aee83edb8d878c56a4cb03aa16570989e734377e4e8739dd1b7d7e,2026-03-26 15:18:00+00:00,False,null,null,null,null,null
7,0x89b5899619d93a180d38011b8aec849deea3f573,0x89b5899619d93a180d38011b8aec849deea3f573,True,False,True,PDP,True,https://mainnet-pdp.infrafolio.com,C=US;ST=Texas;L=Austin,US,Texas,Austin,0x0000000000000000000000000000000000000000,1048576,1073741824,83300000000000000,30,True,True,0x002408011220295ed42035299e74ea5743cc52a1d00a782351a700abd804de06199436ed911c,90,90.0,testing,"{""capacityTib"":""0x3930"",""serviceStatus"":""0x74657374696e67"",""IPNIPeerID"":""0x002408011220295ed42035299e74ea5743cc52a1d00a782351a700abd804de06199436ed911c"",""ipniIpfs"":""0x01"",""ipniPiece"":""0x01"",""paymentTokenAddress"":""0x0000000000000000000000000000000000000000"",""location"":""0x433d55533b53543d54657861733b4c3d41757374696e"",""minProvingPeriodInEpochs"":""0x1e"",""storagePricePerTibPerDay"":""0x0127f0e89dca4000"",""maxPieceSizeInBytes"":""0x40000000"",""minPieceSizeInBytes"":""0x100000"",""serviceURL"":""0x68747470733a2f2f6d61696e6e65742d7064702e696e667261666f6c696f2e636f6d""}",5482846,0x85d6c4cdeb7104168b7a7888a36c2c73f1224442a0638ca807933c04b3462e04,2025-11-10 16:23:00+00:00,5482858,0x1600836de3729985fe9efd52f545228dee0bb2d251f429bba4f08847cfea6cec,2025-11-10 16:29:00+00:00,True,5865704,2026-03-23 14:52:00+00:00,5865704,0x71a2f0fb50af07ec51c1bda943f6c8baf6fe9f7a8a0a95276675ac8d08fc774f,2026-03-23 14:52:00+00:00
1,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,0x32c90c26bca6ed3945de9b29ba4e19d38314d618,True,False,True,PDP,True,https://main.ezpdpz.net,C=GB;ST=Gloucestershire;L=Cheltenham,GB,Gloucestershire,Cheltenham,0x0000000000000000000000000000000000000000,1048576,2147483648,83333333333333330,30,True,True,0x0024080112201dcb0e9feaf9a369c13ccbb8f0c91921afcde832f957020c13f67cd8fb9ad4f1,10,10.0,testing,"{""serviceStatus"":""0x74657374696e67"",""capacityTib"":""0x3130"",""IPNIPeerID"":""0x0024080112201dcb0e9feaf9a369c13ccbb8f0c91921afcde832f957020c13f67cd8fb9ad4f1"",""ipniPeerId"":""0x0024080112201dcb0e9feaf9a369c13ccbb8f0c91921afcde832f957020c13f67cd8fb9ad4f1"",""ipniIpfs"":""0x01"",""ipniPiece"":""0x01"",""paymentTokenAddress"":""0x0000000000000000000000000000000000000000"",""location"":""0x433d47423b53543d476c6f7563657374657273686972653b4c3d4368656c74656e68616d"",""minProvingPeriodInEpochs"":""0x1e"",""storagePricePerTibPerDay"":""0x01280f39a3485552"",""maxPieceSizeInBytes"":""0x80000000"",""minPieceSizeInBytes"":""0x100000"",""serviceURL"":""0x68747470733a2f2f6d61696e2e657a7064707a2e6e6574""}",5462468,0x9f0f508355403a1141bf8be4e389d5d1edbbe9f5b57158dd9e694531a98f1825,2025-11-03 14:34:00+00:00,5821285,0xc71cdb16b2fbe88756c3816f13d3b8cfd541e6fd7835b442cfea8a5e15b947f3,2026-03-08 04:42:30+00:00,True,5464743,2025-11-04 09:31:30+00:00,5464743,0xfe009d2d0746f8180ff7e0cc1f69d07412a93a70991a65ee68061215e9f037e7,2025-11-04 09:31:30+00:00
25,0x7b7fd1531767736acb4fbb5b20a5aba8c675028a,0x7b7fd1531767736acb4fbb5b20a5aba8c675028a,True,False,True,PDP,True,https://storacha.network,earth,null,null,null,0x7b7fd1531767736acb4fbb5b20a5aba8c675028a,1,1,1,1,null,null,null,null,null,null,"{""paymentTokenAddress"":""0x7b7fd1531767736acb4fbb5b20a5aba8c675028a"",""location"":""0x6561727468"",""minProvingPeriodInEpochs"":""0x01"",""storagePricePerTibPerDay"":""0x01"",""maxPieceSizeInBytes"":""0x01"",""minPieceSizeInBytes"":""0x01"",""serviceURL"":""0x68747470733a2f2f73746f72616368612e6e6574776f726b""}",5549432,0x9fa2b6db8d630aba1fa5967eb6f31b381bed42e5614890576e0cfe8dcdd057de,2025-12-03 19:16:00+00:00,5549432,0x9fa2b6db8d630aba1fa5967eb6f31b381bed42e5614890576e0cfe8dcdd057de,2025-12-03 19:16:00+00:00,False,null,null,null,null,null
19,0x21f15b5a2711ef55d9463cf66cc793eb17ce087f,0x21f15b5a2711ef55d9463cf66cc793eb17ce087f,True,False,True,PDP,True,https://storacha.network,earth,null,null,null,0x21f15b5a2711ef55d9463cf66cc793eb17ce087f,1,1,1,1,null,null,null,null,null,null,"{""paymentTokenAddress"":""0x21f15b5a2711ef55d9463cf66cc793eb17ce087f"",""location"":""0x6561727468"",""minProvingPeriodInEpochs"":""0x01"",""storagePricePerTibPerDay"":""0x01"",""maxPieceSizeInBytes"":""0x01"",""minPieceSizeInBytes"":""0x01"",""serviceURL"":""0x68747470733a2f2f73746f72616368612e6e6574776f726b""}",5535854,0x4baa606cadf93908dec2736947e13cf91554d2d851a53e758d6ccaaacd8787ca,2025-11-29 02:07:00+00:00,5535854,0x4baa606cadf93908dec2736947e13cf91554d2d851a53e758d6ccaaacd8787ca,2025-11-29 02:07:00+00:00,False,null,null,null,null,null
27,0xe686d370d8e53f72e543dafe978da41e7e0505cc,0xe686d370d8e53f72e543dafe978da41e7e0505cc,True,False,True,PDP,True,https://storacha.network,earth,null,null,null,0xe686d370d8e53f72e543dafe978da41e7e0505cc,1,1,1,1,null,null,null,null,null,null,"{""paymentTokenAddress"":""0xe686d370d8e53f72e543dafe978da41e7e0505cc"",""location"":""0x6561727468"",""minProvingPeriodInEpochs"":""0x01"",""storagePricePerTibPerDay"":""0x01"",""maxPieceSizeInBytes"":""0x01"",""minPieceSizeInBytes"":""0x01"",""serviceURL"":""0x68747470733a2f2f73746f72616368612e6e6574776f726b""}",5724026,0xbf9bf3f6492f1b36cfa8c187befbc99b9c915caf6616a9f7814e8fbaee310b68,2026-02-02 10:13:00+00:00,5724026,0xbf9bf3f6492f1b36cfa8c187befbc99b9c915caf6616a9f7814e8fbaee310b68,2026-02-02 10:13:00+00:00,False,null,null,null,null,null
21,0x3fa2a4c02478f1e57d3dd2868484164647c45038,0x3fa2a4c02478f1e57d3dd2868484164647c45038,True,False,True,PDP,True,https://storacha.network,earth,null,null,null,0x3fa2a4c02478f1e57d3dd2868484164647c45038,1,1,1,1,null,null,null,null,null,null,"{""paymentTokenAddress"":""0x3fa2a4c02478f1e57d3dd2868484164647c45038"",""location"":""0x6561727468"",""minProvingPeriodInEpochs"":""0x01"",""storagePricePerTibPerDay"":""0x01"",""maxPieceSizeInBytes"":""0x01"",""minPieceSizeInBytes"":""0x01"",""serviceURL"":""0x68747470733a2f2f73746f72616368612e6e6574776f726b""}",5543204,0x65b202618e4abda7774d050adb9d620e62efc0e88782728f71de8a270f3ad1e8,2025-12-01 15:22:00+00:00,5543204,0x65b202618e4abda7774d050adb9d620e62efc0e88782728f71de8a270f3ad1e8,2025-12-01 15:22:00+00:00,False,null,null,null,null,null
8,0xa4440add7c5d9baa1859cde7cd83b88816bc1362,0xa4440add7c5d9baa1859cde7cd83b88816bc1362,True,False,True,PDP,True,http://116.182.20.74:12310,C=US;ST=California;L=San Francisco,US,California,San Francisco,0x0000000000000000000000000000000000000000,1048576,1073741824,83333333333333330,30,True,True,0x0024080112200cbe9eba1bb1f9140df2b7ba22fd503b1a3cfcc409a32f044d5709de0d861450,1,1.0,testing,"{""serviceStatus"":""0x74657374696e67"",""capacityTib"":""0x31"",""IPNIPeerID"":""0x0024080112200cbe9eba1bb1f9140df2b7ba22fd503b1a3cfcc409a32f044d5709de0d861450"",""ipniIpfs"":""0x01"",""ipniPiece"":""0x01"",""paymentTokenAddress"":""0x0000000000000000000000000000000000000000"",""location"":""0x433d55533b53543d43616c69666f726e69613b4c3d53616e204672616e636973636f"",""minProvingPeriodInEpochs"":""0x1e"",""storagePricePerTibPerDay"":""0x01280f39a3485552"",""maxPieceSizeInBytes"":""0x40000000"",""minPieceSizeInBytes"":""0x100000"",""serviceURL"":""0x687474703a2f2f3131362e3138322e32302e37343a3132333130""}",5484390,0x6dea3d6afc40f508ead658ac1b52087bfe29c59fb11169aa6e46c143594fb272,2025-11-11 05:15:00+00:00,5484398,0xccf6beb922a5597fb4939be006f571f3afc4b3408d8e8117b0dd2d69bf7e3298,2025-11-11 05:19:00+00:00,False,null,null,null,null,null
```
