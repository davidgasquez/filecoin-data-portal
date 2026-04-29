-- asset.description = Filecoin clients metrics and latest details.

-- asset.depends = raw.datacapstats_verified_clients
-- asset.depends = model.verified_claims

-- asset.column = client_id | Filecoin client actor id address.
-- asset.column = first_claim_at | Timestamp of the first successful verified claim.
-- asset.column = last_claim_at | Timestamp of the most recent successful verified claim.
-- asset.column = verified_claims | Total successful verified claims.
-- asset.column = verified_providers | Providers with at least one successful verified claim.
-- asset.column = verified_data_onboarded_tibs | Verified data successfully claimed, in tebibytes.
-- asset.column = client_address | Filecoin client address from DatacapStats.
-- asset.column = client_name | Client name from DatacapStats.
-- asset.column = organization_name | Organization name from DatacapStats.
-- asset.column = region | Region from DatacapStats.
-- asset.column = industry | Industry from DatacapStats.
-- asset.column = website | Website from DatacapStats.
-- asset.column = initial_datacap_tibs | Initial datacap allowance, in tebibytes.
-- asset.column = current_datacap_tibs | Current datacap allowance, in tebibytes.
-- asset.column = allocator_id | Latest allocator actor id address.
-- asset.column = allocator_name | Latest allocator name.
-- asset.column = deal_count | Deal count from DatacapStats.
-- asset.column = provider_count | Provider count from DatacapStats.
-- asset.column = top_provider | Top provider from DatacapStats.
-- asset.column = received_datacap_change_tibs | Received datacap change, in tebibytes.
-- asset.column = used_datacap_change_tibs | Used datacap change, in tebibytes.
-- asset.column = used_datacap_tibs | Used datacap, in tebibytes.
-- asset.column = remaining_datacap_tibs | Remaining datacap, in tebibytes.
-- asset.column = datacap_issue_created_at | Datacap issue creation timestamp.
-- asset.column = datacap_message_created_at | Datacap message creation timestamp.
-- asset.column = datacap_retries | DatacapStats retry counter.

-- asset.not_null = client_id
-- asset.unique = client_id

with claims_by_client as (
    select
        client_id,
        min(claim_at) as first_claim_at,
        max(claim_at) as last_claim_at,
        count(*) as verified_claims,
        count(distinct provider_id) as verified_providers,
        sum(piece_size_tibs) as verified_data_onboarded_tibs
    from model.verified_claims
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
        nullif(website, '') as website,
        try_cast(initial_allowance as double) / power(1024, 4) as initial_datacap_tibs,
        coalesce(try_cast(allowance as double), 0) / power(1024, 4) as current_datacap_tibs,
        verifier_address_id as allocator_id,
        nullif(verifier_name, '') as allocator_name,
        try_cast(deal_count as bigint) as deal_count,
        try_cast(provider_count as bigint) as provider_count,
        nullif(top_provider, '') as top_provider,
        try_cast(received_datacap_change as double) / power(1024, 4) as received_datacap_change_tibs,
        try_cast(used_datacap_change as double) / power(1024, 4) as used_datacap_change_tibs,
        try_cast(used_datacap as double) / power(1024, 4) as used_datacap_tibs,
        try_cast(remaining_datacap as double) / power(1024, 4) as remaining_datacap_tibs,
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
    c.verified_claims,
    c.verified_providers,
    c.verified_data_onboarded_tibs,
    d.client_address,
    d.client_name,
    d.organization_name,
    d.region,
    d.industry,
    d.website,
    d.initial_datacap_tibs,
    d.current_datacap_tibs,
    d.allocator_id,
    d.allocator_name,
    d.deal_count,
    d.provider_count,
    d.top_provider,
    d.received_datacap_change_tibs,
    d.used_datacap_change_tibs,
    d.used_datacap_tibs,
    d.remaining_datacap_tibs,
    d.datacap_issue_created_at,
    d.datacap_message_created_at,
    d.datacap_retries
from claims_by_client as c
left join datacap_clients as d
    on try_cast(substr(c.client_id, 3) as bigint) = d.numeric_client_id
order by last_claim_at desc
