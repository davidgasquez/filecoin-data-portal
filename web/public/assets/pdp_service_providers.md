# main.pdp_service_providers

Published PDP service providers.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/pdp/service_providers.sql`
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
| `registered_date` | `DATE` | UTC registration date. |  |
| `product_updated_block` | `BIGINT` | Latest PDP product lifecycle block. |  |
| `product_updated_transaction_hash` | `VARCHAR` | Latest PDP product lifecycle transaction hash. |  |
| `product_updated_date` | `DATE` | UTC latest PDP product lifecycle date. |  |
| `is_fwss_approved` | `BOOLEAN` | Whether the latest FWSS approval event is approved. |  |
| `fwss_first_approved_block` | `BIGINT` | First FWSS approval block, if any. |  |
| `fwss_first_approved_date` | `DATE` | UTC first FWSS approval date, if any. |  |
| `fwss_last_approval_block` | `BIGINT` | Latest FWSS approval block, if any. |  |
| `fwss_last_approval_transaction_hash` | `VARCHAR` | Latest FWSS approval transaction hash, if any. |  |
| `fwss_last_approval_date` | `DATE` | UTC latest FWSS approval date, if any. |  |

## Sample (10 rows)

```csv
provider_id,service_provider,payee,is_registered,is_removed,is_active,product_type,offers_pdp_storage,service_url,location,location_country_code,location_region,location_city,payment_token_address,min_piece_size_bytes,max_piece_size_bytes,storage_price_per_tib_per_day,min_proving_period_epochs,supports_ipni_piece,supports_ipni_ipfs,ipni_peer_id_hex,capacity_tib_text,capacity_tib,service_status,capabilities_json,registered_block,registered_transaction_hash,registered_date,product_updated_block,product_updated_transaction_hash,product_updated_date,is_fwss_approved,fwss_first_approved_block,fwss_first_approved_date,fwss_last_approval_block,fwss_last_approval_transaction_hash,fwss_last_approval_date
19,0x21f15b5a2711ef55d9463cf66cc793eb17ce087f,0x21f15b5a2711ef55d9463cf66cc793eb17ce087f,True,False,True,PDP,True,https://storacha.network,earth,null,null,null,0x21f15b5a2711ef55d9463cf66cc793eb17ce087f,1,1,1,1,null,null,null,null,null,null,"{""paymentTokenAddress"":""0x21f15b5a2711ef55d9463cf66cc793eb17ce087f"",""location"":""0x6561727468"",""minProvingPeriodInEpochs"":""0x01"",""storagePricePerTibPerDay"":""0x01"",""maxPieceSizeInBytes"":""0x01"",""minPieceSizeInBytes"":""0x01"",""serviceURL"":""0x68747470733a2f2f73746f72616368612e6e6574776f726b""}",5535854,0x4baa606cadf93908dec2736947e13cf91554d2d851a53e758d6ccaaacd8787ca,2025-11-29,5535854,0x4baa606cadf93908dec2736947e13cf91554d2d851a53e758d6ccaaacd8787ca,2025-11-29,False,null,null,null,null,null
8,0xa4440add7c5d9baa1859cde7cd83b88816bc1362,0xa4440add7c5d9baa1859cde7cd83b88816bc1362,True,False,True,PDP,True,http://116.182.20.74:12310,C=US;ST=California;L=San Francisco,US,California,San Francisco,0x0000000000000000000000000000000000000000,1048576,1073741824,83333333333333330,30,True,True,0x0024080112200cbe9eba1bb1f9140df2b7ba22fd503b1a3cfcc409a32f044d5709de0d861450,1,1.0,testing,"{""serviceStatus"":""0x74657374696e67"",""capacityTib"":""0x31"",""IPNIPeerID"":""0x0024080112200cbe9eba1bb1f9140df2b7ba22fd503b1a3cfcc409a32f044d5709de0d861450"",""ipniIpfs"":""0x01"",""ipniPiece"":""0x01"",""paymentTokenAddress"":""0x0000000000000000000000000000000000000000"",""location"":""0x433d55533b53543d43616c69666f726e69613b4c3d53616e204672616e636973636f"",""minProvingPeriodInEpochs"":""0x1e"",""storagePricePerTibPerDay"":""0x01280f39a3485552"",""maxPieceSizeInBytes"":""0x40000000"",""minPieceSizeInBytes"":""0x100000"",""serviceURL"":""0x687474703a2f2f3131362e3138322e32302e37343a3132333130""}",5484390,0x6dea3d6afc40f508ead658ac1b52087bfe29c59fb11169aa6e46c143594fb272,2025-11-11,5484398,0xccf6beb922a5597fb4939be006f571f3afc4b3408d8e8117b0dd2d69bf7e3298,2025-11-11,False,null,null,null,null,null
13,0x40dbb5c4dc728b9d5f23444a1e5449d655ce0224,0x40dbb5c4dc728b9d5f23444a1e5449d655ce0224,True,False,True,PDP,True,https://curio.akave.xyz,C=US;ST=Texas;L=Dallas,US,Texas,Dallas,0x0000000000000000000000000000000000000000,1048576,68719476736,83333333333333330,1440,True,True,0x002408011220111c71c31b084ff774b23ecc0f6796fc9d2b084920e049dca56cbee72575ad2a,350,350.0,testing,"{""capacityTib"":""0x333530"",""serviceStatus"":""0x74657374696e67"",""IPNIPeerID"":""0x002408011220111c71c31b084ff774b23ecc0f6796fc9d2b084920e049dca56cbee72575ad2a"",""ipniIpfs"":""0x01"",""ipniPiece"":""0x01"",""paymentTokenAddress"":""0x0000000000000000000000000000000000000000"",""location"":""0x433d55533b53543d54657861733b4c3d44616c6c6173"",""minProvingPeriodInEpochs"":""0x05a0"",""storagePricePerTibPerDay"":""0x01280f39a3485552"",""maxPieceSizeInBytes"":""0x1000000000"",""minPieceSizeInBytes"":""0x100000"",""serviceURL"":""0x68747470733a2f2f637572696f2e616b6176652e78797a""}",5494281,0x46dfc7c0b766a7293e70278a8d1ae9338b718bc99c0fcc1d47ed01c93584bb45,2025-11-14,5512634,0xcbfb1c358bd2c092d7a341379cfa2ee84cf750f2f031cecfe595440e4d89396c,2025-11-21,False,null,null,null,null,null
18,0x4de3d41c4fc6a80c9a5c908f3c6f4e48975637fd,0x4de3d41c4fc6a80c9a5c908f3c6f4e48975637fd,True,False,True,PDP,True,https://storacha.network,earth,null,null,null,0x4de3d41c4fc6a80c9a5c908f3c6f4e48975637fd,1,1,1,1,null,null,null,null,null,null,"{""paymentTokenAddress"":""0x4de3d41c4fc6a80c9a5c908f3c6f4e48975637fd"",""location"":""0x6561727468"",""minProvingPeriodInEpochs"":""0x01"",""storagePricePerTibPerDay"":""0x01"",""maxPieceSizeInBytes"":""0x01"",""minPieceSizeInBytes"":""0x01"",""serviceURL"":""0x68747470733a2f2f73746f72616368612e6e6574776f726b""}",5535714,0x5327e820ed39045e15c47fc11903e69b7da122aae06cfe0e968f8842aaada2c6,2025-11-29,5535714,0x5327e820ed39045e15c47fc11903e69b7da122aae06cfe0e968f8842aaada2c6,2025-11-29,False,null,null,null,null,null
10,0x74075b4a9e00304c2dddbae4a76399830c917544,0x74075b4a9e00304c2dddbae4a76399830c917544,True,False,True,PDP,True,https://mokanla.meje.dev,C=NG;ST=Lagos;L=Lagos,NG,Lagos,Lagos,0x0000000000000000000000000000000000000000,1048576,1073741824,83333333333333330,30,True,True,0x00240801122024a43e835a090adfcdcb65b95c6f934a345e4e206562f66888faeccc1ae98111,1,1.0,testing,"{""capacityTib"":""0x31"",""serviceStatus"":""0x74657374696e67"",""IPNIPeerID"":""0x00240801122024a43e835a090adfcdcb65b95c6f934a345e4e206562f66888faeccc1ae98111"",""ipniIpfs"":""0x01"",""ipniPiece"":""0x01"",""paymentTokenAddress"":""0x0000000000000000000000000000000000000000"",""location"":""0x433d4e473b53543d4c61676f733b4c3d4c61676f73"",""minProvingPeriodInEpochs"":""0x1e"",""storagePricePerTibPerDay"":""0x01280f39a3485552"",""maxPieceSizeInBytes"":""0x40000000"",""minPieceSizeInBytes"":""0x100000"",""serviceURL"":""0x68747470733a2f2f6d6f6b616e6c612e6d656a652e646576""}",5488948,0x133bec4c34cd4566d5771fd25770e311ec5ab325ead44842026558828e37150a,2025-11-12,5724256,0x92b0a31ad528d5ca5078c4eaf64a8e92440e7ceea67eaba4bc5e24d914e9f494,2026-02-02,False,null,null,null,null,null
24,0x55bc49caca448bb810710edbf5cec721ff8ebad2,0x55bc49caca448bb810710edbf5cec721ff8ebad2,True,False,True,PDP,True,https://storacha.network,earth,null,null,null,0x55bc49caca448bb810710edbf5cec721ff8ebad2,1,1,1,1,null,null,null,null,null,null,"{""paymentTokenAddress"":""0x55bc49caca448bb810710edbf5cec721ff8ebad2"",""location"":""0x6561727468"",""minProvingPeriodInEpochs"":""0x01"",""storagePricePerTibPerDay"":""0x01"",""maxPieceSizeInBytes"":""0x01"",""minPieceSizeInBytes"":""0x01"",""serviceURL"":""0x68747470733a2f2f73746f72616368612e6e6574776f726b""}",5548350,0xb01d27cf170c58e2d4131ad7dc2d367f81e05946bbbd48f5622065b2e38c7129,2025-12-03,5548350,0xb01d27cf170c58e2d4131ad7dc2d367f81e05946bbbd48f5622065b2e38c7129,2025-12-03,False,null,null,null,null,null
4,0x67b8a4df8afb983d24646ad7c3035e58be5cdffe,0x67b8a4df8afb983d24646ad7c3035e58be5cdffe,True,False,True,PDP,True,http://pdp.tigerteches.org:5521,C=CN;ST=California;L=San Francisco,CN,California,San Francisco,0x0000000000000000000000000000000000000000,1048576,1073741824,833000000000000000,30,True,True,0x0024080112203276426764730c2eda8660ef8caaeaca459120328bd8ff13593c6ab7ed911d82,10,10.0,testing,"{""serviceStatus"":""0x74657374696e67"",""capacityTib"":""0x3130"",""IPNIPeerID"":""0x0024080112203276426764730c2eda8660ef8caaeaca459120328bd8ff13593c6ab7ed911d82"",""ipniIpfs"":""0x01"",""ipniPiece"":""0x01"",""paymentTokenAddress"":""0x0000000000000000000000000000000000000000"",""location"":""0x433d434e3b53543d43616c69666f726e69613b4c3d53616e204672616e636973636f"",""minProvingPeriodInEpochs"":""0x1e"",""storagePricePerTibPerDay"":""0x0b8f691629e68000"",""maxPieceSizeInBytes"":""0x40000000"",""minPieceSizeInBytes"":""0x100000"",""serviceURL"":""0x687474703a2f2f7064702e74696765727465636865732e6f72673a35353231""}",5479238,0x8713f4aa6212dd0da518e4ccaf95976cbb858160f30890fbd72677c01478f7c4,2025-11-09,5505746,0xe0a17c2dee0eae922ad531da53f9e0a145dd438ee8c41e87d94dfd87629167b5,2025-11-18,False,null,null,null,null,null
23,0x3de6c9f2a3b1009f18431f6124009a6d12ff3537,0x3de6c9f2a3b1009f18431f6124009a6d12ff3537,True,False,True,PDP,True,https://storacha.network,earth,null,null,null,0x3de6c9f2a3b1009f18431f6124009a6d12ff3537,1,1,1,1,null,null,null,null,null,null,"{""paymentTokenAddress"":""0x3de6c9f2a3b1009f18431f6124009a6d12ff3537"",""location"":""0x6561727468"",""minProvingPeriodInEpochs"":""0x01"",""storagePricePerTibPerDay"":""0x01"",""maxPieceSizeInBytes"":""0x01"",""minPieceSizeInBytes"":""0x01"",""serviceURL"":""0x68747470733a2f2f73746f72616368612e6e6574776f726b""}",5545887,0x12ab8add29da8682ddf9f1b2b519eeecdebd0c4c8d0527f16cf8f3f1cb9fc166,2025-12-02,5545887,0x12ab8add29da8682ddf9f1b2b519eeecdebd0c4c8d0527f16cf8f3f1cb9fc166,2025-12-02,False,null,null,null,null,null
20,0xc1aba8ce560ad630c5a640cc4ec8a434327616d9,0xc1aba8ce560ad630c5a640cc4ec8a434327616d9,True,False,True,PDP,True,https://storacha.network,earth,null,null,null,0xc1aba8ce560ad630c5a640cc4ec8a434327616d9,1,1,1,1,null,null,null,null,null,null,"{""paymentTokenAddress"":""0xc1aba8ce560ad630c5a640cc4ec8a434327616d9"",""location"":""0x6561727468"",""minProvingPeriodInEpochs"":""0x01"",""storagePricePerTibPerDay"":""0x01"",""maxPieceSizeInBytes"":""0x01"",""minPieceSizeInBytes"":""0x01"",""serviceURL"":""0x68747470733a2f2f73746f72616368612e6e6574776f726b""}",5537693,0x24ebe319f569b6b5e5d17536d64f340eddc3725e15010a954376c866c69cd7d5,2025-11-29,5537693,0x24ebe319f569b6b5e5d17536d64f340eddc3725e15010a954376c866c69cd7d5,2025-11-29,False,null,null,null,null,null
12,0xa77da4ec1e07eb65bd3a00bd8db62e072a21e8f4,0xa77da4ec1e07eb65bd3a00bd8db62e072a21e8f4,True,False,True,PDP,True,https://warp.filecoin.no,C=NO;ST=Oslo;L=Oslo,NO,Oslo,Oslo,0x0000000000000000000000000000000000000000,1048576,1073741824,83333333333333330,30,True,True,0x0024080112209227e1691bef23c6e77b3a9ebf63a68f062e062c7e4b71cc971e9af3d919c4df,77,77.0,testing,"{""capacityTib"":""0x3737"",""serviceStatus"":""0x74657374696e67"",""IPNIPeerID"":""0x0024080112209227e1691bef23c6e77b3a9ebf63a68f062e062c7e4b71cc971e9af3d919c4df"",""ipniIpfs"":""0x01"",""ipniPiece"":""0x01"",""paymentTokenAddress"":""0x0000000000000000000000000000000000000000"",""location"":""0x433d4e4f3b53543d4f736c6f3b4c3d4f736c6f"",""minProvingPeriodInEpochs"":""0x1e"",""storagePricePerTibPerDay"":""0x01280f39a3485552"",""maxPieceSizeInBytes"":""0x40000000"",""minPieceSizeInBytes"":""0x100000"",""serviceURL"":""0x68747470733a2f2f776172702e66696c65636f696e2e6e6f""}",5494092,0x56b8e9b2fb06034e5a93f98a2f85df3171db2d4e7b1f272615f18f21f554b7bb,2025-11-14,5494127,0xb64cb09cffe9d64cac11b38ac5619e7078ff792f154b0718d39cf0ded04d191e,2025-11-14,False,null,null,null,null,null
```
