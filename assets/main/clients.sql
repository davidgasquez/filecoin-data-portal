-- asset.description = Filecoin clients metrics and latest details.

-- asset.depends = raw.cdp_clients
-- asset.depends = model.verified_claims

-- asset.column = client_id | Filecoin client actor id address.
-- asset.column = first_claim_at | Timestamp of the first successful verified claim.
-- asset.column = last_claim_at | Timestamp of the most recent successful verified claim.
-- asset.column = verified_claims | Total successful verified claims.
-- asset.column = verified_storage_providers | Providers with at least one successful verified claim.
-- asset.column = verified_data_onboarded_tibs | Verified data successfully claimed, in tebibytes.
-- asset.column = client_address | Filecoin client address.
-- asset.column = client_name | Client name.
-- asset.column = application_url | Client application URL.
-- asset.column = datacap_received_tibs | Datacap received, in tebibytes.
-- asset.column = datacap_remaining_tibs | Datacap remaining, in tebibytes.
-- asset.column = datacap_used_2_weeks_tibs | Datacap used in the last two weeks, in tebibytes.
-- asset.column = datacap_used_90_days_tibs | Datacap used in the last 90 days, in tebibytes.

-- asset.not_null = client_id
-- asset.unique = client_id

with claims_by_client as (
    select
        client_id,
        min(claim_at) as first_claim_at,
        max(claim_at) as last_claim_at,
        count(*) as verified_claims,
        count(distinct provider_id) as verified_storage_providers,
        sum(piece_size_tibs) as verified_data_onboarded_tibs
    from model.verified_claims
    group by 1
),
cdp_clients as (
    select
        id as client_id,
        nullif(address, '') as client_address,
        nullif(name, '') as client_name,
        nullif(application_url, '') as application_url,
        try_cast(datacap_received as double) / power(1024, 4) as datacap_received_tibs,
        try_cast(datacap_remaining as double) / power(1024, 4) as datacap_remaining_tibs,
        try_cast(datacap_used_2_weeks as double) / power(1024, 4) as datacap_used_2_weeks_tibs,
        try_cast(datacap_used_90_days as double) / power(1024, 4) as datacap_used_90_days_tibs
    from raw.cdp_clients
)
select
    c.client_id,
    c.first_claim_at,
    c.last_claim_at,
    c.verified_claims,
    c.verified_storage_providers,
    c.verified_data_onboarded_tibs,
    d.client_address,
    d.client_name,
    d.application_url,
    d.datacap_received_tibs,
    d.datacap_remaining_tibs,
    d.datacap_used_2_weeks_tibs,
    d.datacap_used_90_days_tibs
from claims_by_client as c
left join cdp_clients as d using (client_id)
order by last_claim_at desc
