-- asset.description = Current storage provider power.

-- asset.resource = bigquery.lily

-- asset.column = provider_id | Filecoin storage provider actor id address.
-- asset.column = raw_power_tibs | Latest raw byte power, in tebibytes.
-- asset.column = quality_adjusted_power_tibs | Latest quality adjusted power, in tebibytes.
-- asset.column = has_power | Whether the provider currently has positive power.

-- asset.not_null = provider_id
-- asset.unique = provider_id

select
    miner_id as provider_id,
    cast(raw_byte_power as float64) / pow(1024, 4) as raw_power_tibs,
    cast(quality_adj_power as float64) / pow(1024, 4)
        as quality_adjusted_power_tibs,
    true as has_power
from `power_actor_claims`
qualify row_number() over (
    partition by miner_id
    order by height desc
) = 1
and (
    cast(raw_byte_power as int64) > 0
    or cast(quality_adj_power as int64) > 0
)
