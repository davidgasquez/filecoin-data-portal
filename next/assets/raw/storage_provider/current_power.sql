-- asset.description = Filecoin storage provider latest power data.
-- asset.resource = bigquery.lily

-- asset.column = provider_id | Filecoin storage provider miner actor id address.
-- asset.column = current_raw_power_tibs | Latest observed raw byte power.
-- asset.column = current_quality_adjusted_power_tibs | Latest quality adjusted power.
-- asset.column = has_current_power | Whether the provider currently has power.

-- asset.not_null = provider_id
-- asset.unique = provider_id

select
    miner_id as provider_id,
    cast(raw_byte_power as float64) / pow(1024, 4) as current_raw_power_tibs,
    cast(quality_adj_power as float64) / pow(1024, 4)
        as current_quality_adjusted_power_tibs,
    true as has_current_power
from `power_actor_claims`
qualify row_number() over (
    partition by miner_id
    order by height desc
) = 1
and (
    cast(raw_byte_power as int64) > 0
    or cast(quality_adj_power as int64) > 0
)
order by provider_id
