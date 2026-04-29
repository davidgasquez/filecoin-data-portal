-- asset.description = Daily verified claims by client and provider.

-- asset.depends = model.verified_claims

-- asset.column = date | UTC claim date.
-- asset.column = client_id | Filecoin client actor id address.
-- asset.column = provider_id | Filecoin storage provider actor id address.
-- asset.column = verified_data_onboarded_tibs | Verified data claimed on the date, in tebibytes.
-- asset.column = verified_claims | Successful verified claims on the date.

-- asset.not_null = date
-- asset.not_null = client_id
-- asset.not_null = provider_id
-- asset.not_null = verified_data_onboarded_tibs
-- asset.not_null = verified_claims
-- asset.assert = verified_data_onboarded_tibs > 0
-- asset.assert = verified_claims > 0

select
    date,
    client_id,
    provider_id,
    sum(piece_size_tibs) as verified_data_onboarded_tibs,
    count(*) as verified_claims
from model.verified_claims
where date <= current_date - 1
group by 1, 2, 3
order by date desc
