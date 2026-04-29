-- asset.description = Successful verified claims normalized to Filecoin addresses and TiB.

-- asset.depends = raw.verified_registry_claims

-- asset.column = claim_at | Successful verified claim timestamp.
-- asset.column = date | UTC claim date.
-- asset.column = client_id | Filecoin client actor id address.
-- asset.column = provider_id | Filecoin storage provider actor id address.
-- asset.column = piece_size_tibs | Verified piece size, in tebibytes.

-- asset.not_null = claim_at
-- asset.not_null = date
-- asset.not_null = client_id
-- asset.not_null = provider_id
-- asset.not_null = piece_size_tibs
-- asset.assert = piece_size_tibs > 0

with normalized as (
    select
        to_timestamp((claim_epoch * 30) + 1598306400) at time zone 'UTC' as claim_at,
        'f0' || cast(client_id as varchar) as client_id,
        'f0' || cast(provider_id as varchar) as provider_id,
        cast(piece_size_bytes as double) / power(1024, 4) as piece_size_tibs
    from raw.verified_registry_claims
)
select
    claim_at,
    date(claim_at) as date,
    client_id,
    provider_id,
    piece_size_tibs
from normalized
