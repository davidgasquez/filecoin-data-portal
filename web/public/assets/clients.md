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
f03290407,2024-12-29 11:09:30+00:00,2026-04-18 23:59:30+00:00,293573,29,9174.15625,f1llzvof7lq7amv6lfnumtj2uhz5dnhbswh7vvkaq,zzflk,null,China,"Information, Media & Telecommunications",http://www.zzflk.com/,10752.0,878.84375,f03012911,Marshall-Fil-Data-Pathway,null,null,null,0.0,47.46875,9873.15625,878.84375,null,2026-03-20 07:06:00+00:00,3
f03759102,2026-03-03 14:37:00+00:00,2026-04-18 23:59:30+00:00,84495,6,5280.9375,f1wr4csvsjcuiemkjbp4k44qu5hsywhwshgfcnz7i,"立遺伝学研究所 (National Institute of Genetics, Japan)",null,Japan,Life Science / Healthcare,null,6912.0,1376.5,f03018029,NonEntropy,null,null,null,2048.0,1690.5625,5535.5,1376.5,null,2026-04-13 02:40:30+00:00,3
f03535091,2025-05-09 12:11:00+00:00,2026-04-18 23:59:30+00:00,105822,4,3306.8671875,f3r3tkbr34pcrzj42hy2pc7e4ujpxhrmuohy4bapnommhzmnn7vlyn6e5jb2lqpddsjtitzeicjcm2a4cypspa,null,null,null,null,null,965.9200000000001,344.4140625,f03760270,Ramo Cloud,null,null,null,0.0,177.09375,621.5059375000001,344.4140625,null,2026-03-06 21:23:30+00:00,3
f03253574,2025-02-11 21:28:30+00:00,2026-04-18 23:55:00+00:00,29358,9,917.3518829345703,f410fqslkkgx5ehy4qnghg6uhy55exo2tg5mpck7jpri,null,null,null,null,null,788.0,382.1551513671875,f03015757,FIDL Enterprise Data,null,null,null,0.0,0.0,405.8448486328125,382.1551513671875,null,2025-03-21 11:30:30+00:00,3
f03136439,2025-03-05 01:58:30+00:00,2026-04-18 23:50:00+00:00,91749,3,2867.15625,f3svae653c6zetlcghrg6e2zc33fyg56imqcj2y35ornyji6kh7vwp7vgteptjfulkes4j4zloocfusj6vctia,Aitrainer,null,China,IT & Technology Services,https://commoncrawl.org/,5084.0,1121.7691040039062,f03019859,Herony,null,null,null,0.0,171.5,3962.2308959960938,1121.7691040039062,null,2025-11-10 09:49:30+00:00,3
f03091977,2024-07-30 07:39:00+00:00,2026-04-18 23:40:30+00:00,8700,29,263.17321395874023,f1hnvljphtrpwb6pxszxoh7k57br7goo33s6b22ry,PrelingerArchives LLC,null,null,null,null,370.0,35.40099334716797,f02943486,FF Social Impact,377,1,100,0.0,6.900390625,334.59900665283203,35.40099334716797,null,2025-05-14 15:42:30+00:00,3
f03183111,2024-08-28 02:39:30+00:00,2026-04-18 22:43:00+00:00,102462,2,3200.531862258911,f1p2p3e6gv6vygtouazdcb4757vh5leylcxggzkbq,TheStarling Lab,null,null,null,null,3742.6399999999994,1164.8112627410883,f03015757,FIDL Enterprise Data,null,null,null,0.0,9.5,2577.828737258911,1164.8112627410883,null,2026-02-26 12:38:00+00:00,3
f03200311,2024-09-19 16:03:00+00:00,2026-04-18 22:24:00+00:00,1388,24,43.375,f1ggmci7w2weizhh36uqetihmh76ewgme6hwgowti,Lighthouse,null,null,null, [lighthouse.storage](https://lighthouse.storage/),60.0,12.0,f02824311,datacap-data-preparation-and-onboarding,null,null,null,0.0,0.34375,48.0,12.0,null,2026-03-31 06:09:30+00:00,3
f03542902,2025-04-27 09:50:00+00:00,2026-04-18 20:37:30+00:00,140343,12,4385.71875,f17qnsd4mirtgjimjkhna2yuyhr5b6xkrwcq6z2zi,Xmov,null,China,IT & Technology Services,https://www.xmov.ai/home,3840.0,35.28125,f03012494,Storify Data Fortress,null,null,null,0.0,499.9375,3804.71875,35.28125,null,2026-03-05 14:49:30+00:00,3
f03644104,2026-04-05 13:49:00+00:00,2026-04-18 20:21:00+00:00,17223,2,538.21875,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null
```
