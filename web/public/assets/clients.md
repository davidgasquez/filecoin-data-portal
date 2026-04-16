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
f03759102,2026-03-03 15:37:00+01:00,2026-04-15 01:59:30+02:00,78971,6,4935.6875,f1wr4csvsjcuiemkjbp4k44qu5hsywhwshgfcnz7i,"立遺伝学研究所 (National Institute of Genetics, Japan)",null,Japan,Life Science / Healthcare,null,6912.0,1776.5,f03018029,NonEntropy,null,null,null,2048.0,1658.0,5135.5,1776.5,null,2026-04-13 04:40:30+02:00,3
f03644104,2026-04-05 15:49:00+02:00,2026-04-15 01:58:30+02:00,13892,2,434.125,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null
f03535091,2025-05-09 14:11:00+02:00,2026-04-15 01:54:00+02:00,103682,4,3239.9921875,f3r3tkbr34pcrzj42hy2pc7e4ujpxhrmuohy4bapnommhzmnn7vlyn6e5jb2lqpddsjtitzeicjcm2a4cypspa,null,null,null,null,null,965.9200000000001,427.8828125,f03760270,Ramo Cloud,null,null,null,0.0,118.5,538.0371875000001,427.8828125,null,2026-03-06 22:23:30+01:00,3
f03136439,2025-03-05 02:58:30+01:00,2026-04-15 01:48:30+02:00,90083,3,2815.09375,f3svae653c6zetlcghrg6e2zc33fyg56imqcj2y35ornyji6kh7vwp7vgteptjfulkes4j4zloocfusj6vctia,Aitrainer,null,China,IT & Technology Services,https://commoncrawl.org/,5084.0,1172.9566040039062,f03019859,Herony,null,null,null,0.0,168.53125,3911.0433959960938,1172.9566040039062,null,2025-11-10 10:49:30+01:00,3
f03253574,2025-02-11 22:28:30+01:00,2026-04-14 20:50:30+02:00,28796,9,899.7893829345703,f410fqslkkgx5ehy4qnghg6uhy55exo2tg5mpck7jpri,null,null,null,null,null,788.0,382.1551513671875,f03015757,FIDL Enterprise Data,null,null,null,0.0,0.0,405.8448486328125,382.1551513671875,null,2025-03-21 12:30:30+01:00,3
f03770592,2026-04-13 01:16:00+02:00,2026-04-14 15:17:30+02:00,10,3,0.3125,f1nk464agzj7eta4x74vq3q4bwww7khcevxiiysma,null,null,null,null,null,10.0,9.65625,f03019296,datacap-decentralized-onboarding-to-the-mix,null,null,null,10.0,0.3125,0.34375,9.65625,null,2026-04-12 13:17:00+02:00,3
f03768208,2026-04-13 20:16:00+02:00,2026-04-14 09:20:30+02:00,148,2,4.625,f1p3ulfjhxxf7yzblx2uyqpcsjuimhh64nrouwi2i,null,null,null,null,null,10.0,5.375,f03019296,datacap-decentralized-onboarding-to-the-mix,null,null,null,10.0,4.625,4.625,5.375,null,2026-04-02 18:00:30+02:00,3
f03644598,2025-09-08 12:15:30+02:00,2026-04-14 05:35:30+02:00,6680,4,208.75,f1nplitd46e2m5woeiwlcjqu7kri66hr2rx4sywvi,null,null,null,null,** [https://aurorainfra.ai/](https://aurorainfra.ai/)  ,410.0,196.53125,f03019298,datacap-decentralized-onboarding-to-self-selected-sps,null,null,null,0.0,3.1875,213.46875,196.53125,null,2025-10-15 13:36:00+02:00,3
f03542902,2025-04-27 11:50:00+02:00,2026-04-14 03:10:30+02:00,138922,11,4341.3125,f17qnsd4mirtgjimjkhna2yuyhr5b6xkrwcq6z2zi,Xmov,null,China,IT & Technology Services,https://www.xmov.ai/home,3840.0,79.84375,f03012494,Storify Data Fortress,null,null,null,0.0,825.9375,3760.15625,79.84375,null,2026-03-05 15:49:30+01:00,3
f03770671,2026-04-13 20:20:00+02:00,2026-04-13 20:22:30+02:00,2,2,0.0625,f1fnrnv6sowdr6sabqn6o2i73rao4veri63hnhe6i,null,null,null,null,null,10.0,9.9375,f03019296,datacap-decentralized-onboarding-to-the-mix,null,null,null,10.0,0.0625,0.0625,9.9375,null,2026-04-12 19:35:30+02:00,3
```
