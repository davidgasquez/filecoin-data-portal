-- asset.description = Daily total verified data onboarded on Filecoin.

-- asset.depends = raw.verified_registry_claims

-- asset.column = date | UTC day when verified data was successfully claimed/onboarded.
-- asset.column = verified_data_onboarded_bytes | Sum of verified piece sizes claimed on the day, in bytes.
-- asset.column = verified_data_onboarded_pibs | Sum of verified piece sizes claimed on the day, in pebibytes.
-- asset.column = verified_claims | Number of successful verified registry claims on the day.
-- asset.column = unique_clients | Distinct clients with at least one successful verified claim on the day.
-- asset.column = unique_providers | Distinct providers with at least one successful verified claim on the day.

-- asset.not_null = date
-- asset.unique = date

select
    date(to_timestamp((claim_epoch * 30) + 1598306400)) as date,
    sum(piece_size_bytes) as verified_data_onboarded_bytes,
    cast(sum(piece_size_bytes) as double) / power(1024, 5) as verified_data_onboarded_pibs,
    count(*) as verified_claims,
    count(distinct client_id) as unique_clients,
    count(distinct provider_id) as unique_providers
from raw.verified_registry_claims
group by 1
order by 1
