# main.clients

Published clients.

- asset code: `https://github.com/davidgasquez/filecoin-data-portal/blob/main/assets/main/clients.sql`
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
f01151139,2023-03-24 10:17:30+01:00,2023-09-10 08:31:30+02:00,4155,15,129.84375,f3watks6wyq5sakerofowyv7q4gwx4z6ukmfe2irh5zitspj6gpceudt3rrbvm5psofkcgoabev3s2mwtkcunq,NFTStorage,null,null,null,null,2125.0,2000.0,f02049625,LDN v3.1 multisig,4000,10,66.4,0.0,0.0,125.0,2000.0,null,2023-11-23 05:23:00+01:00,3
f01174487,2023-02-28 17:37:30+01:00,2023-10-02 23:53:00+02:00,15336,14,344.59375,f1sshymsne7x3cndwflpk57ozerlzkxgzv7aknadq,null,shanghai jinshizichan asset management,null,null, https://www.jinshizichan.cn/,375.0,3.25,f01940930,LDN EFil+,16847,14,16.87,0.0,0.0,371.75,3.25,null,2023-08-24 13:09:00+02:00,3
f01302553,2022-12-31 21:14:30+01:00,2023-03-04 07:51:30+01:00,10424,5,651.5,f3skkellc7wegakh2blqeu4kkrlzuqy2siymwli7sec6eq77c2v4kzgz5ozgnasjl5r52ckameba5kds7hdjda,null,Meizhai Technology,Asia,IT & Technology Services, www.decor.ai,800.0,147.95417594909668,f01858410,LDN v3 multisig,10433,5,53.26,0.0,0.0,652.0458240509033,147.95417594909668,null,2022-09-21 11:03:30+02:00,3
f01471028,2022-11-30 20:01:00+01:00,2023-03-20 05:45:00+01:00,27191,14,849.60546875,f1r3d25hl2y7rqlsu2mgczdethy4qqjmkfdlmibfq,null, NEXRAD - FilSwan,null,null, https://www.filswan.com Slack: http://filswan.slack.com​ Discord: http://discord.gg/Uw5jCGqc,1998.0,271.455078125,f01858410,LDN v3 multisig,55596,44,16.39,0.0,0.0,1726.544921875,271.455078125,null,2022-12-18 12:08:00+01:00,3
f01513505,2023-04-08 01:00:00+02:00,2023-04-08 09:00:00+02:00,690,1,21.5625,f1vmbre2qgafcfizvbmcfdj5k24ouwscp5cavspxi,null,True Elite,null,null, https://metawave.info/,100.0,0.0,f01858410,LDN v3 multisig,2906,5,37.6,0.0,0.0,100.0,0.0,null,2022-08-24 14:25:30+02:00,3
f01524687,2022-11-30 17:56:30+01:00,2023-12-08 01:32:00+01:00,3134,6,84.390625,f3wvmc2kg2zts4ehhjqw5qdagu34cqvtg2rhjynnf3ejojxygyfzq4ypa4gmupfxqu4aqskess3awwk7wtisqq,Glif auto verified,null,null,null,null,0.0625,2.357666015625,f0121877,Jonathan Schwartz,350,2,99.66,0.0,0.0,-2.295166015625,2.357666015625,null,2023-08-16 05:20:00+02:00,-1
f01621962,2022-12-03 04:56:00+01:00,2022-12-04 13:38:00+01:00,25,1,0.703125,f3vtrnj3jlbsdw3u4jtnjf7v5gy7hwjyuaeuzj7aimudpwwuhsg654ytd5344rfi2gwam5jrceb7munoaknh6q,null,IPFSPower - Slingshot Restore,null,Web3,ipfspower,25.0,20.39013671875,f01623281,LDN # 154,176,2,86.28,0.0,0.0,4.60986328125,20.39013671875,2021-12-20 14:34:41+01:00,2021-12-22 01:43:00+01:00,0
f01687339,2022-12-01 01:41:00+01:00,2024-09-02 09:27:00+02:00,22770,8,695.669921875,f1lzkycqjpx4nmvznhxkl5fd7rct26tpo56qx2ura,null,KIM JIN HYUK Gongzakso(meaning: Production),null,null, https://www.facebook.com/gonngzakso,800.0,18.53466796875,f02049625,LDN v3.1 multisig,25082,6,37.27,0.0,11.4189453125,781.46533203125,18.53466796875,null,2023-08-17 09:58:30+02:00,3
f01877976,2022-11-30 15:09:00+01:00,2023-01-11 19:02:30+01:00,20526,12,641.296875,f1euejrtpg5vphqzydzleld2vgxfkhbrueiomz54y,null,Fei Yan - Kernelogic,null,null, https://slingshot.kernelogic.ca/ @feiya200,5118.959999999999,851.7529515838614,f01858410,LDN v3 multisig,145773,32,7.49,0.0,0.0,4267.207048416138,851.7529515838614,null,2022-11-18 06:49:30+01:00,3
f01904773,2022-12-09 23:01:30+01:00,2022-12-24 11:46:30+01:00,1219,5,37.541015625,f1xts6y3lb7mmcjelapapjsvso7yv2cvwip7pozay,null,Chuangshengyun Technology,Asia,IT & Technology Services, https://www.chuangshengyun.info/,60.0,1.861328125,f01858410,LDN v3 multisig,2005,8,20.58,0.0,0.0,58.138671875,1.861328125,null,2022-12-07 09:06:30+01:00,3
```
