# ruff: noqa: E501
# asset.description = Verified Filecoin clients
# asset.materialization = dataframe

# asset.depends = raw.datacapstats_verified_clients

# asset.column = client_id | Filecoin client id address with at least one successful verified claim.
# asset.column = first_claim_at | Timestamp of the first successful verified claim observed for the client.
# asset.column = last_claim_at | Timestamp of the most recent successful verified claim observed for the client.
# asset.column = total_verified_claims | Total successful verified claims observed for the client.
# asset.column = total_verified_providers | Distinct providers with at least one successful verified claim for the client.
# asset.column = total_verified_piece_cids | Distinct claimed piece CIDs observed for the client.
# asset.column = total_verified_data_onboarded_bytes | Total verified bytes successfully claimed for the client.
# asset.column = total_verified_data_onboarded_tibs | Total verified bytes successfully claimed for the client, in tebibytes.
# asset.column = client_address | Filecoin client address from the latest DatacapStats snapshot, if available.
# asset.column = client_name | Client name from the latest DatacapStats snapshot, if available.
# asset.column = organization_name | Client organization name from DatacapStats, if available.
# asset.column = region | Client region from the latest DatacapStats snapshot, if available.
# asset.column = industry | Client industry from the latest DatacapStats snapshot, if available.
# asset.column = client_website | Client website from the latest DatacapStats snapshot, if available.
# asset.column = initial_datacap_bytes | Initial Datacap allowance from the latest DatacapStats snapshot, in bytes.
# asset.column = initial_datacap_tibs | Initial Datacap allowance from the latest DatacapStats snapshot, in tebibytes.
# asset.column = current_datacap_bytes | Current Datacap allowance from the latest DatacapStats snapshot, in bytes.
# asset.column = current_datacap_tibs | Current Datacap allowance from the latest DatacapStats snapshot, in tebibytes.
# asset.column = allocator_id | Latest allocator id address reported by DatacapStats for the client.
# asset.column = verifier_name | Latest allocator display name reported by DatacapStats for the client.
# asset.column = datacap_deal_count | Verified deal count reported by DatacapStats for the client.
# asset.column = datacap_provider_count | Provider count reported by DatacapStats for the client.
# asset.column = top_provider | Top provider reported by DatacapStats for the client.
# asset.column = received_datacap_change_bytes | Received Datacap change from the latest DatacapStats snapshot, in bytes.
# asset.column = received_datacap_change_tibs | Received Datacap change from the latest DatacapStats snapshot, in tebibytes.
# asset.column = used_datacap_change_bytes | Used Datacap change from the latest DatacapStats snapshot, in bytes.
# asset.column = used_datacap_change_tibs | Used Datacap change from the latest DatacapStats snapshot, in tebibytes.
# asset.column = used_datacap_bytes | Used Datacap reported by the latest DatacapStats snapshot, in bytes.
# asset.column = used_datacap_tibs | Used Datacap reported by the latest DatacapStats snapshot, in tebibytes.
# asset.column = reported_remaining_datacap_bytes | Remaining Datacap reported by the latest DatacapStats snapshot, in bytes.
# asset.column = reported_remaining_datacap_tibs | Remaining Datacap reported by the latest DatacapStats snapshot, in tebibytes.
# asset.column = datacap_issue_created_at | Issue creation timestamp from the latest DatacapStats snapshot, if available.
# asset.column = datacap_message_created_at | Datacap message creation timestamp from the latest DatacapStats snapshot, if available.
# asset.column = datacap_retries | Retry counter from the latest DatacapStats snapshot.
# asset.not_null = client_id
# asset.not_null = first_claim_at
# asset.not_null = last_claim_at
# asset.not_null = total_verified_claims
# asset.not_null = total_verified_providers
# asset.not_null = total_verified_piece_cids
# asset.not_null = total_verified_data_onboarded_bytes
# asset.not_null = total_verified_data_onboarded_tibs
# asset.unique = client_id
# asset.assert = total_verified_claims > 0
# asset.assert = total_verified_providers > 0
# asset.assert = total_verified_piece_cids > 0
# asset.assert = total_verified_data_onboarded_bytes > 0
# asset.assert = total_verified_data_onboarded_tibs > 0

import os

import polars as pl
from google.cloud import bigquery

from fdp.api import db_connection
from fdp.google import credentials_from_env

DEFAULT_PROJECT = "protocol-labs-data-nexus"
DEFAULT_LOCATION = "us-east4"

CLAIMS_BY_CLIENT_QUERY = """
with verified_registry_claims as (
    select
        timestamp_seconds((v.height * 30) + 1598306400) as claim_at,
        v.`from` as provider_id,
        concat('f0', json_extract_scalar(claim, '$.Client')) as client_id,
        regexp_extract(json_extract(claim, '$.Data'), '"/":"([^"]+)"', 1) as piece_cid,
        cast(json_extract_scalar(claim, '$.Size') as int64) as piece_size_bytes
    from `lily-data.lily.vm_messages` as v
    cross join unnest(coalesce(json_extract_array(v.params, '$.Sectors'), array<string>[])) as sector
    cross join unnest(coalesce(json_extract_array(sector, '$.Claims'), array<string>[])) as claim
    where v.`to` = 'f06'
      and v.method = 9
      and v.exit_code = 0
      and json_extract_scalar(claim, '$.Client') is not null

    union all

    select
        timestamp_seconds((v.height * 30) + 1598306400) as claim_at,
        v.`from` as provider_id,
        concat('f0', json_extract_scalar(sector, '$.Client')) as client_id,
        regexp_extract(json_extract(sector, '$.Data'), '"/":"([^"]+)"', 1) as piece_cid,
        cast(json_extract_scalar(sector, '$.Size') as int64) as piece_size_bytes
    from `lily-data.lily.vm_messages` as v
    cross join unnest(coalesce(json_extract_array(v.params, '$.Sectors'), array<string>[])) as sector
    where v.`to` = 'f06'
      and v.method = 9
      and v.exit_code = 0
      and json_extract_scalar(sector, '$.Client') is not null
      and array_length(coalesce(json_extract_array(sector, '$.Claims'), array<string>[])) = 0
),
claims_by_client as (
    select
        client_id,
        min(claim_at) as first_claim_at,
        max(claim_at) as last_claim_at,
        count(*) as total_verified_claims,
        count(distinct provider_id) as total_verified_providers,
        count(distinct piece_cid) as total_verified_piece_cids,
        sum(piece_size_bytes) as total_verified_data_onboarded_bytes,
        cast(sum(piece_size_bytes) as float64) / pow(1024, 4) as total_verified_data_onboarded_tibs
    from verified_registry_claims
    group by 1
)
select
    client_id,
    first_claim_at,
    last_claim_at,
    total_verified_claims,
    total_verified_providers,
    total_verified_piece_cids,
    total_verified_data_onboarded_bytes,
    total_verified_data_onboarded_tibs
from claims_by_client
order by last_claim_at desc, client_id
""".strip()


def query_claims_by_client() -> pl.DataFrame:
    client = bigquery.Client(
        project=os.environ.get("FDP_BIGQUERY_PROJECT", DEFAULT_PROJECT),
        location=os.environ.get("FDP_BIGQUERY_LOCATION", DEFAULT_LOCATION),
        credentials=credentials_from_env(),
    )
    job_config = bigquery.QueryJobConfig(
        priority=bigquery.QueryPriority.BATCH,
        allow_large_results=True,
    )
    arrow_table = client.query(CLAIMS_BY_CLIENT_QUERY, job_config=job_config).to_arrow(
        create_bqstorage_client=True
    )
    return pl.DataFrame(arrow_table)


def filecoin_clients() -> pl.DataFrame:
    claims_by_client = query_claims_by_client()

    with db_connection() as conn:
        conn.register("claims_by_client", claims_by_client)
        result = conn.execute(
            """
            with datacap_clients as (
                select
                    address_id as client_id,
                    nullif(address, '') as client_address,
                    nullif(name, '') as client_name,
                    nullif(org_name, '') as organization_name,
                    nullif(region, '') as region,
                    nullif(industry, '') as industry,
                    nullif(website, '') as client_website,
                    try_cast(initial_allowance as bigint) as initial_datacap_bytes,
                    try_cast(initial_allowance as double) / power(1024, 4) as initial_datacap_tibs,
                    coalesce(try_cast(allowance as double), 0) as current_datacap_bytes,
                    coalesce(try_cast(allowance as double), 0) / power(1024, 4) as current_datacap_tibs,
                    verifier_address_id as allocator_id,
                    nullif(verifier_name, '') as verifier_name,
                    try_cast(deal_count as bigint) as datacap_deal_count,
                    try_cast(provider_count as bigint) as datacap_provider_count,
                    nullif(top_provider, '') as top_provider,
                    try_cast(received_datacap_change as double) as received_datacap_change_bytes,
                    try_cast(received_datacap_change as double) / power(1024, 4) as received_datacap_change_tibs,
                    try_cast(used_datacap_change as double) as used_datacap_change_bytes,
                    try_cast(used_datacap_change as double) / power(1024, 4) as used_datacap_change_tibs,
                    try_cast(used_datacap as double) as used_datacap_bytes,
                    try_cast(used_datacap as double) / power(1024, 4) as used_datacap_tibs,
                    try_cast(remaining_datacap as double) as reported_remaining_datacap_bytes,
                    try_cast(remaining_datacap as double) / power(1024, 4) as reported_remaining_datacap_tibs,
                    to_timestamp(try_cast(issue_create_timestamp as double)) as datacap_issue_created_at,
                    to_timestamp(try_cast(create_message_timestamp as double)) as datacap_message_created_at,
                    retries as datacap_retries
                from raw.datacapstats_verified_clients
                qualify row_number() over (
                    partition by address_id
                    order by created_at_height desc nulls last, fetched_at desc
                ) = 1
            )
            select
                c.client_id,
                c.first_claim_at,
                c.last_claim_at,
                c.total_verified_claims,
                c.total_verified_providers,
                c.total_verified_piece_cids,
                c.total_verified_data_onboarded_bytes,
                c.total_verified_data_onboarded_tibs,
                d.client_address,
                d.client_name,
                d.organization_name,
                d.region,
                d.industry,
                d.client_website,
                d.initial_datacap_bytes,
                d.initial_datacap_tibs,
                d.current_datacap_bytes,
                d.current_datacap_tibs,
                d.allocator_id,
                d.verifier_name,
                d.datacap_deal_count,
                d.datacap_provider_count,
                d.top_provider,
                d.received_datacap_change_bytes,
                d.received_datacap_change_tibs,
                d.used_datacap_change_bytes,
                d.used_datacap_change_tibs,
                d.used_datacap_bytes,
                d.used_datacap_tibs,
                d.reported_remaining_datacap_bytes,
                d.reported_remaining_datacap_tibs,
                d.datacap_issue_created_at,
                d.datacap_message_created_at,
                d.datacap_retries
            from claims_by_client as c
            left join datacap_clients as d using (client_id)
            order by c.last_claim_at desc, c.client_id
            """
        ).fetch_arrow_table()

    return pl.DataFrame(result)
