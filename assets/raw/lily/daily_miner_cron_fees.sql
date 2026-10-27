-- asset.description = Daily Filecoin storage provider cron fees and penalties from Lily.
-- asset.resource = bigquery.lily

-- asset.column = date | UTC date.
-- asset.column = storage_provider_cron_burn_fil | FIL burned during storage provider cron events.
-- asset.column = storage_provider_cron_fee_assessed_fil | FIL fees assessed during storage provider cron events.
-- asset.column = storage_provider_cron_penalty_assessed_fil | FIL penalties assessed during storage provider cron events.

-- asset.not_null = date
-- asset.not_null = storage_provider_cron_burn_fil
-- asset.not_null = storage_provider_cron_fee_assessed_fil
-- asset.not_null = storage_provider_cron_penalty_assessed_fil
-- asset.unique = date

select
    date(timestamp_seconds((height * 30) + 1598306400)) as date,
    cast(sum(cast(burn as bignumeric)) / 1e18 as float64)
        as storage_provider_cron_burn_fil,
    cast(sum(cast(fee as bignumeric)) / 1e18 as float64)
        as storage_provider_cron_fee_assessed_fil,
    cast(sum(cast(penalty as bignumeric)) / 1e18 as float64)
        as storage_provider_cron_penalty_assessed_fil
from `miner_cron_fees`
group by 1
order by 1 desc
