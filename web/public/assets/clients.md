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
f03759102,2026-03-03 14:37:00+00:00,2026-04-17 23:59:30+00:00,83245,6,5202.8125,f1wr4csvsjcuiemkjbp4k44qu5hsywhwshgfcnz7i,"立遺伝学研究所 (National Institute of Genetics, Japan)",null,Japan,Life Science / Healthcare,null,6912.0,1576.5,f03018029,NonEntropy,null,null,null,2048.0,1691.25,5335.5,1576.5,null,2026-04-13 02:40:30+00:00,3
f03542902,2025-04-27 09:50:00+00:00,2026-04-17 23:51:30+00:00,139993,12,4374.78125,f17qnsd4mirtgjimjkhna2yuyhr5b6xkrwcq6z2zi,Xmov,null,China,IT & Technology Services,https://www.xmov.ai/home,3840.0,35.28125,f03012494,Storify Data Fortress,null,null,null,0.0,572.0625,3804.71875,35.28125,null,2026-03-05 14:49:30+00:00,3
f03753456,2026-02-17 00:45:00+00:00,2026-04-17 23:50:30+00:00,143759,4,4492.46875,f1i4i2s26mu3zh2tu34emv4l4evodewpfiyw3bheq,"GuangxiShanhai Xingchen Culture Media Co., Ltd.",null,China,"Information, Media & Telecommunications",null,4515.839999999999,0.058749999999236024,f03251444,Starry Manual Allocator,null,null,null,0.0,17.59375,4515.78125,0.058749999999236024,null,2026-02-28 11:04:00+00:00,3
f03644104,2026-04-05 13:49:00+00:00,2026-04-17 23:50:30+00:00,17082,2,533.8125,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null
f03136439,2025-03-05 01:58:30+00:00,2026-04-17 23:49:30+00:00,91317,3,2853.65625,f3svae653c6zetlcghrg6e2zc33fyg56imqcj2y35ornyji6kh7vwp7vgteptjfulkes4j4zloocfusj6vctia,Aitrainer,null,China,IT & Technology Services,https://commoncrawl.org/,5084.0,1133.9566040039062,f03019859,Herony,null,null,null,0.0,169.21875,3950.0433959960938,1133.9566040039062,null,2025-11-10 09:49:30+00:00,3
f03535091,2025-05-09 12:11:00+00:00,2026-04-17 15:58:00+00:00,104888,4,3277.6796875,f3r3tkbr34pcrzj42hy2pc7e4ujpxhrmuohy4bapnommhzmnn7vlyn6e5jb2lqpddsjtitzeicjcm2a4cypspa,null,null,null,null,null,965.9200000000001,384.9453125,f03760270,Ramo Cloud,null,null,null,0.0,150.03125,580.9746875000001,384.9453125,null,2026-03-06 21:23:30+00:00,3
f03644598,2025-09-08 10:15:30+00:00,2026-04-17 15:28:30+00:00,6753,4,211.03125,f1nplitd46e2m5woeiwlcjqu7kri66hr2rx4sywvi,null,null,null,null,** [https://aurorainfra.ai/](https://aurorainfra.ai/)  ,410.0,193.8125,f03019298,datacap-decentralized-onboarding-to-self-selected-sps,null,null,null,0.0,5.03125,216.1875,193.8125,null,2025-10-15 11:36:00+00:00,3
f03253574,2025-02-11 21:28:30+00:00,2026-04-17 14:21:30+00:00,29163,9,911.2581329345703,f410fqslkkgx5ehy4qnghg6uhy55exo2tg5mpck7jpri,null,null,null,null,null,788.0,382.1551513671875,f03015757,FIDL Enterprise Data,null,null,null,0.0,0.0,405.8448486328125,382.1551513671875,null,2025-03-21 11:30:30+00:00,3
f03770592,2026-04-12 23:16:00+00:00,2026-04-17 01:48:30+00:00,11,3,0.34375,f1nk464agzj7eta4x74vq3q4bwww7khcevxiiysma,null,null,null,null,null,10.0,9.625,f03019296,datacap-decentralized-onboarding-to-the-mix,null,null,null,10.0,0.34375,0.375,9.625,null,2026-04-12 11:17:00+00:00,3
f03510418,2025-04-29 03:35:00+00:00,2026-04-17 00:53:00+00:00,62616,3,1941.653389930725,f1skjgotikvvlx3uzhzltiq2ejmwdmtxt5doa5vpy,null,null,null,null,null,1264.0,299.22745990753174,f03015751,FIDL Open Data,null,null,null,0.0,3.250237464904785,964.7725400924683,299.22745990753174,null,2025-09-04 16:40:30+00:00,3
```
