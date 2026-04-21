-- asset.description = Daily metrics for clients.

-- asset.depends = model.daily_verified_claims

-- asset.column = date | UTC claim date.
-- asset.column = client_id | Filecoin client actor id address.
-- asset.column = verified_data_onboarded_tibs | Verified data claimed on the date, in tebibytes.
-- asset.column = verified_claims | Successful verified claims on the date.
-- asset.column = verified_providers | Providers with at least one successful verified claim on the date.

-- asset.not_null = date
-- asset.not_null = client_id
-- asset.not_null = verified_data_onboarded_tibs
-- asset.not_null = verified_claims
-- asset.not_null = verified_providers

select
    date,
    client_id,
    sum(verified_data_onboarded_tibs) as verified_data_onboarded_tibs,
    sum(verified_claims) as verified_claims,
    count(distinct provider_id) as verified_providers
from model.daily_verified_claims
group by 1, 2
order by date desc
