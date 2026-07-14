-- asset.description = Daily base fee statistics.
-- asset.resource = bigquery.lily

-- asset.column = date | UTC date.
-- asset.column = base_fee_avg_nano_fil_per_gas | Average base fee per gas unit, in nanoFIL.
-- asset.column = base_fee_min_nano_fil_per_gas | Minimum base fee per gas unit, in nanoFIL.
-- asset.column = base_fee_max_nano_fil_per_gas | Maximum base fee per gas unit, in nanoFIL.

-- asset.not_null = date
-- asset.not_null = base_fee_avg_nano_fil_per_gas
-- asset.not_null = base_fee_min_nano_fil_per_gas
-- asset.not_null = base_fee_max_nano_fil_per_gas
-- asset.unique = date
-- asset.assert = base_fee_min_nano_fil_per_gas <= base_fee_avg_nano_fil_per_gas
-- asset.assert = base_fee_avg_nano_fil_per_gas <= base_fee_max_nano_fil_per_gas

with base_fees as (
    select
        date(timestamp_seconds((height * 30) + 1598306400)) as date,
        cast(base_fee as bignumeric) * 1e9 as base_fee_nano_fil_per_gas
    from `message_gas_economy`
    where date(timestamp_seconds((height * 30) + 1598306400)) < current_date()
)
select
    date,
    cast(avg(base_fee_nano_fil_per_gas) as float64)
        as base_fee_avg_nano_fil_per_gas,
    cast(min(base_fee_nano_fil_per_gas) as float64)
        as base_fee_min_nano_fil_per_gas,
    cast(max(base_fee_nano_fil_per_gas) as float64)
        as base_fee_max_nano_fil_per_gas
from base_fees
group by 1
order by date desc
