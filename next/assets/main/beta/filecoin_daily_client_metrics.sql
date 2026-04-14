-- asset.description = Daily Filecoin client metrics from verified claims, with sparse client-day rows.

-- asset.depends = raw.verified_registry_claims

-- asset.column = date | UTC day when the client had successful verified claims.
-- asset.column = client_id | Filecoin client actor id address.
-- asset.column = verified_data_onboarded_tibs | Sum of verified piece sizes successfully claimed for the client on the day, in tebibytes.
-- asset.column = verified_claims | Number of successful verified registry claims for the client on the day.
-- asset.column = unique_verified_providers | Distinct providers with at least one successful verified claim for the client on the day.

-- asset.not_null = date
-- asset.not_null = client_id
-- asset.not_null = verified_data_onboarded_tibs
-- asset.not_null = verified_claims
-- asset.not_null = unique_verified_providers
-- asset.assert = verified_data_onboarded_tibs > 0
-- asset.assert = verified_claims > 0
-- asset.assert = unique_verified_providers > 0

select
    date(to_timestamp((claim_epoch * 30) + 1598306400)) as date,
    'f0' || cast(client_id as varchar) as client_id,
    cast(sum(piece_size_bytes) as double) / power(1024, 4)
        as verified_data_onboarded_tibs,
    count(*) as verified_claims,
    count(distinct provider_id) as unique_verified_providers
from raw.verified_registry_claims
group by 1, 2
order by 1 desc, 2
