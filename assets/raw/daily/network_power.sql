-- asset.description = Daily Filecoin network power snapshots from Lily chain powers.
-- asset.resource = bigquery.lily

-- asset.column = date | UTC date.
-- asset.column = raw_power_pibs | End-of-day raw byte power, in pebibytes.
-- asset.column = quality_adjusted_power_pibs | End-of-day quality adjusted power, in pebibytes.

-- asset.not_null = date
-- asset.not_null = raw_power_pibs
-- asset.not_null = quality_adjusted_power_pibs
-- asset.unique = date

select
    date(timestamp_seconds((height * 30) + 1598306400)) as date,
    cast(total_raw_bytes_power as float64) / pow(1024, 5) as raw_power_pibs,
    cast(total_qa_bytes_power as float64) / pow(1024, 5)
        as quality_adjusted_power_pibs
from `chain_powers`
qualify row_number() over (
    partition by date(timestamp_seconds((height * 30) + 1598306400))
    order by height desc
) = 1
order by 1 desc
