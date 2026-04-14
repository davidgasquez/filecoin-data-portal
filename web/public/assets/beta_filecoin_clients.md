# beta_filecoin_clients

Verified Filecoin clients

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/tree/main/next/assets/main/beta/filecoin_clients.sql`
- rows: `1500`

## Depends

- `raw.datacapstats_verified_clients`
- `raw.verified_registry_claims`

## Tests

- `not_null(client_id)`
- `not_null(first_claim_at)`
- `not_null(last_claim_at)`
- `not_null(total_verified_claims)`
- `not_null(total_verified_providers)`
- `not_null(total_verified_data_onboarded_tibs)`
- `unique(client_id)`
- `assert(total_verified_claims > 0)`
- `assert(total_verified_providers > 0)`
- `assert(total_verified_data_onboarded_tibs > 0)`

## Columns

| column | type | description | tests |
|---|---|---|---|
| `client_id` | `VARCHAR` | Filecoin client id address with at least one successful verified claim. | `not_null`, `unique` |
| `first_claim_at` | `TIMESTAMP WITH TIME ZONE` | Timestamp of the first successful verified claim observed for the client. | `not_null` |
| `last_claim_at` | `TIMESTAMP WITH TIME ZONE` | Timestamp of the most recent successful verified claim observed for the client. | `not_null` |
| `total_verified_claims` | `BIGINT` | Total successful verified claims observed for the client. | `not_null` |
| `total_verified_providers` | `BIGINT` | Distinct providers with at least one successful verified claim for the client. | `not_null` |
| `total_verified_data_onboarded_tibs` | `DOUBLE` | Total verified bytes successfully claimed for the client, in tebibytes. | `not_null` |
| `client_address` | `VARCHAR` | Filecoin client address from the latest DatacapStats snapshot, if available. |  |
| `client_name` | `VARCHAR` | Client name from the latest DatacapStats snapshot, if available. |  |
| `organization_name` | `VARCHAR` | Client organization name from DatacapStats, if available. |  |
| `region` | `VARCHAR` | Client region from the latest DatacapStats snapshot, if available. |  |
| `industry` | `VARCHAR` | Client industry from the latest DatacapStats snapshot, if available. |  |
| `client_website` | `VARCHAR` | Client website from the latest DatacapStats snapshot, if available. |  |
| `initial_datacap_tibs` | `DOUBLE` | Initial Datacap allowance from the latest DatacapStats snapshot, in tebibytes. |  |
| `current_datacap_tibs` | `DOUBLE` | Current Datacap allowance from the latest DatacapStats snapshot, in tebibytes. |  |
| `allocator_id` | `VARCHAR` | Latest allocator id address reported by DatacapStats for the client. |  |
| `verifier_name` | `VARCHAR` | Latest allocator display name reported by DatacapStats for the client. |  |
| `datacap_deal_count` | `BIGINT` | Verified deal count reported by DatacapStats for the client. |  |
| `datacap_provider_count` | `BIGINT` | Provider count reported by DatacapStats for the client. |  |
| `top_provider` | `VARCHAR` | Top provider reported by DatacapStats for the client. |  |
| `received_datacap_change_tibs` | `DOUBLE` | Received Datacap change from the latest DatacapStats snapshot, in tebibytes. |  |
| `used_datacap_change_tibs` | `DOUBLE` | Used Datacap change from the latest DatacapStats snapshot, in tebibytes. |  |
| `used_datacap_tibs` | `DOUBLE` | Used Datacap reported by the latest DatacapStats snapshot, in tebibytes. |  |
| `reported_remaining_datacap_tibs` | `DOUBLE` | Remaining Datacap reported by the latest DatacapStats snapshot, in tebibytes. |  |
| `datacap_issue_created_at` | `TIMESTAMP WITH TIME ZONE` | Issue creation timestamp from the latest DatacapStats snapshot, if available. |  |
| `datacap_message_created_at` | `TIMESTAMP WITH TIME ZONE` | Datacap message creation timestamp from the latest DatacapStats snapshot, if available. |  |
| `datacap_retries` | `BIGINT` | Retry counter from the latest DatacapStats snapshot. |  |

## Sample (10 rows)

```csv
client_id,first_claim_at,last_claim_at,total_verified_claims,total_verified_providers,total_verified_data_onboarded_tibs,client_address,client_name,organization_name,region,industry,client_website,initial_datacap_tibs,current_datacap_tibs,allocator_id,verifier_name,datacap_deal_count,datacap_provider_count,top_provider,received_datacap_change_tibs,used_datacap_change_tibs,used_datacap_tibs,reported_remaining_datacap_tibs,datacap_issue_created_at,datacap_message_created_at,datacap_retries
f03759102,2026-03-03 15:37:00+01:00,2026-04-14 01:59:30+02:00,76264,6,4766.5,f1wr4csvsjcuiemkjbp4k44qu5hsywhwshgfcnz7i,"立遺伝学研究所 (National Institute of Genetics, Japan)",null,Japan,Life Science / Healthcare,null,6912.0,1776.5,f03018029,NonEntropy,null,null,null,2048.0,1565.8125,5135.5,1776.5,null,2026-04-13 04:40:30+02:00,3
f03768208,2026-04-13 20:16:00+02:00,2026-04-14 01:57:00+02:00,75,2,2.34375,f1p3ulfjhxxf7yzblx2uyqpcsjuimhh64nrouwi2i,null,null,null,null,null,10.0,5.375,f03019296,datacap-decentralized-onboarding-to-the-mix,null,null,null,10.0,2.3125,4.625,5.375,null,2026-04-02 18:00:30+02:00,3
f03644104,2026-04-05 15:49:00+02:00,2026-04-14 01:55:30+02:00,10515,2,328.59375,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null
f03253574,2025-02-11 22:28:30+01:00,2026-04-14 01:50:00+02:00,28579,9,893.0081329345703,f410fqslkkgx5ehy4qnghg6uhy55exo2tg5mpck7jpri,null,null,null,null,null,788.0,382.1551513671875,f03015757,FIDL Enterprise Data,null,null,null,0.0,0.0,405.8448486328125,382.1551513671875,null,2025-03-21 12:30:30+01:00,3
f03136439,2025-03-05 02:58:30+01:00,2026-04-14 01:48:30+02:00,89691,3,2802.84375,f3svae653c6zetlcghrg6e2zc33fyg56imqcj2y35ornyji6kh7vwp7vgteptjfulkes4j4zloocfusj6vctia,Aitrainer,null,China,IT & Technology Services,https://commoncrawl.org/,5084.0,1187.1753540039062,f03019859,Herony,null,null,null,0.0,169.8125,3896.8246459960938,1187.1753540039062,null,2025-11-10 10:49:30+01:00,3
f03542902,2025-04-27 11:50:00+02:00,2026-04-13 20:54:00+02:00,138920,11,4341.25,f17qnsd4mirtgjimjkhna2yuyhr5b6xkrwcq6z2zi,Xmov,null,China,IT & Technology Services,https://www.xmov.ai/home,3840.0,79.84375,f03012494,Storify Data Fortress,null,null,null,0.0,927.71875,3760.15625,79.84375,null,2026-03-05 15:49:30+01:00,3
f03770592,2026-04-13 01:16:00+02:00,2026-04-13 20:22:30+02:00,7,3,0.21875,f1nk464agzj7eta4x74vq3q4bwww7khcevxiiysma,null,null,null,null,null,10.0,9.65625,f03019296,datacap-decentralized-onboarding-to-the-mix,null,null,null,10.0,0.21875,0.34375,9.65625,null,2026-04-12 13:17:00+02:00,3
f03770671,2026-04-13 20:20:00+02:00,2026-04-13 20:22:30+02:00,2,2,0.0625,f1fnrnv6sowdr6sabqn6o2i73rao4veri63hnhe6i,null,null,null,null,null,10.0,9.9375,f03019296,datacap-decentralized-onboarding-to-the-mix,null,null,null,10.0,0.0625,0.0625,9.9375,null,2026-04-12 19:35:30+02:00,3
f03644598,2025-09-08 12:15:30+02:00,2026-04-13 05:36:30+02:00,6675,4,208.59375,f1nplitd46e2m5woeiwlcjqu7kri66hr2rx4sywvi,null,null,null,null,** [https://aurorainfra.ai/](https://aurorainfra.ai/)  ,410.0,196.71875,f03019298,datacap-decentralized-onboarding-to-self-selected-sps,null,null,null,0.0,3.21875,213.28125,196.71875,null,2025-10-15 13:36:00+02:00,3
f03753456,2026-02-17 01:45:00+01:00,2026-04-13 05:24:00+02:00,143204,4,4475.125,f1i4i2s26mu3zh2tu34emv4l4evodewpfiyw3bheq,"GuangxiShanhai Xingchen Culture Media Co., Ltd.",null,China,"Information, Media & Telecommunications",null,4515.839999999999,30.058749999999236,f03251444,Starry Manual Allocator,null,null,null,0.0,0.9375,4485.78125,30.058749999999236,null,2026-02-28 12:04:00+01:00,3
```
