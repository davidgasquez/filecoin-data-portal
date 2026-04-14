-- asset.description = Daily verified claim metrics by Filecoin storage
-- provider.

-- asset.depends = raw.verified_registry_claims

-- asset.column = date | UTC day when verified data was successfully
-- claimed/onboarded.
-- asset.column = provider_id | Filecoin storage provider miner actor id
-- address.
-- asset.column = verified_data_onboarded_tibs | Sum of verified piece sizes
-- claimed by the provider on the day, in tebibytes.
-- asset.column = verified_claims | Number of successful verified registry
-- claims by the provider on the day.
-- asset.column = unique_verified_clients | Distinct verified clients with at
-- least one successful claim with the provider on the day.

-- asset.not_null = date
-- asset.not_null = provider_id
-- asset.not_null = verified_data_onboarded_tibs
-- asset.not_null = verified_claims
-- asset.not_null = unique_verified_clients
-- asset.assert = verified_data_onboarded_tibs >= 0
-- asset.assert = verified_claims >= 0
-- asset.assert = unique_verified_clients >= 0

select
    date(to_timestamp((claim_epoch * 30) + 1598306400)) as date,
    'f0' || cast(provider_id as varchar) as provider_id,
    cast(sum(piece_size_bytes) as double) / power(1024, 4)
        as verified_data_onboarded_tibs,
    count(*) as verified_claims,
    count(distinct client_id) as unique_verified_clients
from raw.verified_registry_claims
group by 1, 2
order by 1, 2
