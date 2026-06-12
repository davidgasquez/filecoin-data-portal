-- asset.description = Daily network burn components.

-- asset.depends = raw.daily_network_burn
-- asset.depends = raw.daily_storage_provider_cron_fees
-- asset.depends = model.daily_network_activity

-- asset.column = date | UTC date.
-- asset.column = total_burn_fil | Total FIL burned on-chain.
-- asset.column = message_gas_burn_fil | FIL burned by message base fees and over-estimation.
-- asset.column = message_storage_provider_penalty_fil | FIL penalties incurred by storage providers during message execution.
-- asset.column = storage_provider_cron_burn_fil | FIL burned during storage provider cron events.
-- asset.column = storage_provider_cron_fee_assessed_fil | FIL fees assessed during storage provider cron events.
-- asset.column = storage_provider_cron_penalty_assessed_fil | FIL penalties assessed during storage provider cron events.
-- asset.column = unattributed_burn_fil | FIL burned by other mechanisms.

-- asset.not_null = date
-- asset.not_null = total_burn_fil
-- asset.not_null = message_gas_burn_fil
-- asset.not_null = message_storage_provider_penalty_fil
-- asset.not_null = storage_provider_cron_burn_fil
-- asset.not_null = storage_provider_cron_fee_assessed_fil
-- asset.not_null = storage_provider_cron_penalty_assessed_fil
-- asset.not_null = unattributed_burn_fil
-- asset.unique = date

select
    network_burn.date,
    network_burn.total_burn_fil,
    coalesce(network_activity.message_burn_fil, 0) as message_gas_burn_fil,
    coalesce(network_activity.message_storage_provider_penalty_fil, 0)
        as message_storage_provider_penalty_fil,
    coalesce(storage_provider_cron_fees.storage_provider_cron_burn_fil, 0)
        as storage_provider_cron_burn_fil,
    coalesce(
        storage_provider_cron_fees.storage_provider_cron_fee_assessed_fil,
        0
    ) as storage_provider_cron_fee_assessed_fil,
    coalesce(
        storage_provider_cron_fees.storage_provider_cron_penalty_assessed_fil,
        0
    ) as storage_provider_cron_penalty_assessed_fil,
    network_burn.total_burn_fil
        - coalesce(network_activity.message_burn_fil, 0)
        - coalesce(network_activity.message_storage_provider_penalty_fil, 0)
        - coalesce(storage_provider_cron_fees.storage_provider_cron_burn_fil, 0)
        as unattributed_burn_fil
from raw.daily_network_burn as network_burn
left join raw.daily_storage_provider_cron_fees as storage_provider_cron_fees
    using (date)
left join model.daily_network_activity as network_activity
    using (date)
order by date desc
