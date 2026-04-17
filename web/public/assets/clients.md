# main.clients

Published clients.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/clients.sql`
- dataset url: `https://data.filecoindataportal.xyz/clients.parquet`
- rows: `1500`

## Depends

- `raw.datacapstats_verified_clients`
- `raw.verified_registry_claims`

## Tests

- `not_null(client_id)`
- `unique(client_id)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `client_id` | `VARCHAR` | Filecoin client actor id address. | `not_null`, `unique` |
| `first_claim_at` | `TIMESTAMP WITH TIME ZONE` | Timestamp of the first successful verified claim. |  |
| `last_claim_at` | `TIMESTAMP WITH TIME ZONE` | Timestamp of the most recent successful verified claim. |  |
| `verified_claims` | `BIGINT` | Total successful verified claims. |  |
| `verified_providers` | `BIGINT` | Providers with at least one successful verified claim. |  |
| `verified_data_onboarded_tibs` | `DOUBLE` | Verified data successfully claimed, in tebibytes. |  |
| `client_address` | `VARCHAR` | Filecoin client address from DatacapStats. |  |
| `client_name` | `VARCHAR` | Client name from DatacapStats. |  |
| `organization_name` | `VARCHAR` | Organization name from DatacapStats. |  |
| `region` | `VARCHAR` | Region from DatacapStats. |  |
| `industry` | `VARCHAR` | Industry from DatacapStats. |  |
| `website` | `VARCHAR` | Website from DatacapStats. |  |
| `initial_datacap_tibs` | `DOUBLE` | Initial datacap allowance, in tebibytes. |  |
| `current_datacap_tibs` | `DOUBLE` | Current datacap allowance, in tebibytes. |  |
| `allocator_id` | `VARCHAR` | Latest allocator actor id address. |  |
| `allocator_name` | `VARCHAR` | Latest allocator name. |  |
| `deal_count` | `BIGINT` | Deal count from DatacapStats. |  |
| `provider_count` | `BIGINT` | Provider count from DatacapStats. |  |
| `top_provider` | `VARCHAR` | Top provider from DatacapStats. |  |
| `received_datacap_change_tibs` | `DOUBLE` | Received datacap change, in tebibytes. |  |
| `used_datacap_change_tibs` | `DOUBLE` | Used datacap change, in tebibytes. |  |
| `used_datacap_tibs` | `DOUBLE` | Used datacap, in tebibytes. |  |
| `remaining_datacap_tibs` | `DOUBLE` | Remaining datacap, in tebibytes. |  |
| `datacap_issue_created_at` | `TIMESTAMP WITH TIME ZONE` | Datacap issue creation timestamp. |  |
| `datacap_message_created_at` | `TIMESTAMP WITH TIME ZONE` | Datacap message creation timestamp. |  |
| `datacap_retries` | `BIGINT` | DatacapStats retry counter. |  |

## Sample (10 rows)

```csv
client_id,first_claim_at,last_claim_at,verified_claims,verified_providers,verified_data_onboarded_tibs,client_address,client_name,organization_name,region,industry,website,initial_datacap_tibs,current_datacap_tibs,allocator_id,allocator_name,deal_count,provider_count,top_provider,received_datacap_change_tibs,used_datacap_change_tibs,used_datacap_tibs,remaining_datacap_tibs,datacap_issue_created_at,datacap_message_created_at,datacap_retries
f03759102,2026-03-03 14:37:00+00:00,2026-04-16 23:58:00+00:00,81995,6,5124.6875,f1wr4csvsjcuiemkjbp4k44qu5hsywhwshgfcnz7i,"立遺伝学研究所 (National Institute of Genetics, Japan)",null,Japan,Life Science / Healthcare,null,6912.0,1576.5,f03018029,NonEntropy,null,null,null,2048.0,1690.6875,5335.5,1576.5,null,2026-04-13 02:40:30+00:00,3
f03644104,2026-04-05 13:49:00+00:00,2026-04-16 23:56:30+00:00,15606,2,487.6875,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null
f03535091,2025-05-09 12:11:00+00:00,2026-04-16 23:52:00+00:00,104490,4,3265.2421875,f3r3tkbr34pcrzj42hy2pc7e4ujpxhrmuohy4bapnommhzmnn7vlyn6e5jb2lqpddsjtitzeicjcm2a4cypspa,null,null,null,null,null,965.9200000000001,403.8828125,f03760270,Ramo Cloud,null,null,null,0.0,138.0,562.0371875000001,403.8828125,null,2026-03-06 21:23:30+00:00,3
f03253574,2025-02-11 21:28:30+00:00,2026-04-16 23:50:00+00:00,29095,9,909.1331329345703,f410fqslkkgx5ehy4qnghg6uhy55exo2tg5mpck7jpri,null,null,null,null,null,788.0,382.1551513671875,f03015757,FIDL Enterprise Data,null,null,null,0.0,0.0,405.8448486328125,382.1551513671875,null,2025-03-21 11:30:30+00:00,3
f03136439,2025-03-05 01:58:30+00:00,2026-04-16 23:49:30+00:00,90899,3,2840.59375,f3svae653c6zetlcghrg6e2zc33fyg56imqcj2y35ornyji6kh7vwp7vgteptjfulkes4j4zloocfusj6vctia,Aitrainer,null,China,IT & Technology Services,https://commoncrawl.org/,5084.0,1150.4566040039062,f03019859,Herony,null,null,null,0.0,168.375,3933.5433959960938,1150.4566040039062,null,2025-11-10 09:49:30+00:00,3
f03542902,2025-04-27 09:50:00+00:00,2026-04-16 23:42:00+00:00,138927,12,4341.46875,f17qnsd4mirtgjimjkhna2yuyhr5b6xkrwcq6z2zi,Xmov,null,China,IT & Technology Services,https://www.xmov.ai/home,3840.0,54.1875,f03012494,Storify Data Fortress,null,null,null,0.0,647.28125,3785.8125,54.1875,null,2026-03-05 14:49:30+00:00,3
f03510418,2025-04-29 03:35:00+00:00,2026-04-16 23:36:30+00:00,62601,3,1941.6533460617065,f1skjgotikvvlx3uzhzltiq2ejmwdmtxt5doa5vpy,null,null,null,null,null,1264.0,299.22745990753174,f03015751,FIDL Open Data,null,null,null,0.0,4.6876935958862305,964.7725400924683,299.22745990753174,null,2025-09-04 16:40:30+00:00,3
f03753456,2026-02-17 00:45:00+00:00,2026-04-16 23:32:30+00:00,143205,4,4475.15625,f1i4i2s26mu3zh2tu34emv4l4evodewpfiyw3bheq,"GuangxiShanhai Xingchen Culture Media Co., Ltd.",null,China,"Information, Media & Telecommunications",null,4515.839999999999,15.808749999999236,f03251444,Starry Manual Allocator,null,null,null,0.0,0.84375,4500.03125,15.808749999999236,null,2026-02-28 11:04:00+00:00,3
f03644598,2025-09-08 10:15:30+00:00,2026-04-16 06:54:00+00:00,6695,4,209.21875,f1nplitd46e2m5woeiwlcjqu7kri66hr2rx4sywvi,null,null,null,null,** [https://aurorainfra.ai/](https://aurorainfra.ai/)  ,410.0,193.9375,f03019298,datacap-decentralized-onboarding-to-self-selected-sps,null,null,null,0.0,3.40625,216.0625,193.9375,null,2025-10-15 11:36:00+00:00,3
f03200311,2024-09-19 16:03:00+00:00,2026-04-16 04:55:30+00:00,1387,24,43.34375,f1ggmci7w2weizhh36uqetihmh76ewgme6hwgowti,Lighthouse,null,null,null, [lighthouse.storage](https://lighthouse.storage/),60.0,12.03125,f02824311,datacap-data-preparation-and-onboarding,null,null,null,0.0,0.34375,47.96875,12.03125,null,2026-03-31 06:09:30+00:00,3
```
