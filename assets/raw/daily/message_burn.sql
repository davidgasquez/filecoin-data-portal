-- asset.description = Daily Filecoin message burn from Lily gas outputs.
-- asset.resource = bigquery.lily

-- asset.column = date | UTC date.
-- asset.column = base_fee_burn_fil | Daily FIL burned by base fees, in FIL.
-- asset.column = over_estimation_burn_fil | Daily FIL burned by gas overestimation, in FIL.
-- asset.column = message_burn_fil | Daily FIL burned by exact message gas burn, in FIL.

-- asset.not_null = date
-- asset.not_null = base_fee_burn_fil
-- asset.not_null = over_estimation_burn_fil
-- asset.not_null = message_burn_fil
-- asset.unique = date

select
    date(timestamp_seconds((height * 30) + 1598306400)) as date,
    sum(cast(base_fee_burn as float64)) / 1e18 as base_fee_burn_fil,
    sum(cast(over_estimation_burn as float64)) / 1e18
        as over_estimation_burn_fil,
    sum(
        cast(base_fee_burn as float64)
        + cast(over_estimation_burn as float64)
    ) / 1e18 as message_burn_fil
from `derived_gas_outputs`
group by 1
order by 1 desc
