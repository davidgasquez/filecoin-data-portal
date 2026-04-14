-- asset.description = Verified Filecoin clients

-- asset.depends = raw.datacapstats_verified_clients
-- asset.depends = raw.verified_registry_claims

-- asset.column = client_id | Filecoin client id address with at least one successful verified claim.
-- asset.column = first_claim_at | Timestamp of the first successful verified claim observed for the client.
-- asset.column = last_claim_at | Timestamp of the most recent successful verified claim observed for the client.
-- asset.column = total_verified_claims | Total successful verified claims observed for the client.
-- asset.column = total_verified_providers | Distinct providers with at least one successful verified claim for the client.
-- asset.column = total_verified_data_onboarded_tibs | Total verified bytes successfully claimed for the client, in tebibytes.
-- asset.column = client_address | Filecoin client address from the latest DatacapStats snapshot, if available.
-- asset.column = client_name | Client name from the latest DatacapStats snapshot, if available.
-- asset.column = organization_name | Client organization name from DatacapStats, if available.
-- asset.column = region | Client region from the latest DatacapStats snapshot, if available.
-- asset.column = industry | Client industry from the latest DatacapStats snapshot, if available.
-- asset.column = client_website | Client website from the latest DatacapStats snapshot, if available.
-- asset.column = initial_datacap_tibs | Initial Datacap allowance from the latest DatacapStats snapshot, in tebibytes.
-- asset.column = current_datacap_tibs | Current Datacap allowance from the latest DatacapStats snapshot, in tebibytes.
-- asset.column = allocator_id | Latest allocator id address reported by DatacapStats for the client.
-- asset.column = verifier_name | Latest allocator display name reported by DatacapStats for the client.
-- asset.column = datacap_deal_count | Verified deal count reported by DatacapStats for the client.
-- asset.column = datacap_provider_count | Provider count reported by DatacapStats for the client.
-- asset.column = top_provider | Top provider reported by DatacapStats for the client.
-- asset.column = received_datacap_change_tibs | Received Datacap change from the latest DatacapStats snapshot, in tebibytes.
-- asset.column = used_datacap_change_tibs | Used Datacap change from the latest DatacapStats snapshot, in tebibytes.
-- asset.column = used_datacap_tibs | Used Datacap reported by the latest DatacapStats snapshot, in tebibytes.
-- asset.column = reported_remaining_datacap_tibs | Remaining Datacap reported by the latest DatacapStats snapshot, in tebibytes.
-- asset.column = datacap_issue_created_at | Issue creation timestamp from the latest DatacapStats snapshot, if available.
-- asset.column = datacap_message_created_at | Datacap message creation timestamp from the latest DatacapStats snapshot, if available.
-- asset.column = datacap_retries | Retry counter from the latest DatacapStats snapshot.
-- asset.not_null = client_id
-- asset.not_null = first_claim_at
-- asset.not_null = last_claim_at
-- asset.not_null = total_verified_claims
-- asset.not_null = total_verified_providers
-- asset.not_null = total_verified_data_onboarded_tibs
-- asset.unique = client_id
-- asset.assert = total_verified_claims > 0
-- asset.assert = total_verified_providers > 0
-- asset.assert = total_verified_data_onboarded_tibs > 0

with claims_by_client as (
    select
        client_id,
        min(to_timestamp((claim_epoch * 30) + 1598306400)) as first_claim_at,
        max(to_timestamp((claim_epoch * 30) + 1598306400)) as last_claim_at,
        count(*) as total_verified_claims,
        count(distinct provider_id) as total_verified_providers,
        cast(sum(piece_size_bytes) as double) / power(1024, 4) as total_verified_data_onboarded_tibs
    from raw.verified_registry_claims
    group by 1
),
datacap_clients as (
    select
        case
            when starts_with(address_id, 'f0') then try_cast(substr(address_id, 3) as bigint)
            else null
        end as numeric_client_id,
        nullif(address, '') as client_address,
        nullif(name, '') as client_name,
        nullif(org_name, '') as organization_name,
        nullif(region, '') as region,
        nullif(industry, '') as industry,
        nullif(website, '') as client_website,
        try_cast(initial_allowance as double) / power(1024, 4) as initial_datacap_tibs,
        coalesce(try_cast(allowance as double), 0) / power(1024, 4) as current_datacap_tibs,
        verifier_address_id as allocator_id,
        nullif(verifier_name, '') as verifier_name,
        try_cast(deal_count as bigint) as datacap_deal_count,
        try_cast(provider_count as bigint) as datacap_provider_count,
        nullif(top_provider, '') as top_provider,
        try_cast(received_datacap_change as double) / power(1024, 4) as received_datacap_change_tibs,
        try_cast(used_datacap_change as double) / power(1024, 4) as used_datacap_change_tibs,
        try_cast(used_datacap as double) / power(1024, 4) as used_datacap_tibs,
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
    'f0' || cast(c.client_id as varchar) as client_id,
    c.first_claim_at,
    c.last_claim_at,
    c.total_verified_claims,
    c.total_verified_providers,
    c.total_verified_data_onboarded_tibs,
    d.client_address,
    d.client_name,
    d.organization_name,
    d.region,
    d.industry,
    d.client_website,
    d.initial_datacap_tibs,
    d.current_datacap_tibs,
    d.allocator_id,
    d.verifier_name,
    d.datacap_deal_count,
    d.datacap_provider_count,
    d.top_provider,
    d.received_datacap_change_tibs,
    d.used_datacap_change_tibs,
    d.used_datacap_tibs,
    d.reported_remaining_datacap_tibs,
    d.datacap_issue_created_at,
    d.datacap_message_created_at,
    d.datacap_retries
from claims_by_client as c
left join datacap_clients as d
    on c.client_id = d.numeric_client_id
order by c.last_claim_at desc, c.client_id
