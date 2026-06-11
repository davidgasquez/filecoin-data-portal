-- asset.description = Daily network burn components.

-- asset.depends = raw.daily_network_burn
-- asset.depends = raw.daily_miner_cron_fees
-- asset.depends = model.daily_network_activity

-- asset.column = date | UTC date.
-- asset.column = total_burn_fil | Total FIL burned on-chain.
-- asset.column = message_gas_burn_fil | FIL burned by message base fees and over-estimation.
-- asset.column = message_miner_penalty_burn_fil | FIL burned by message execution miner penalties.
-- asset.column = miner_cron_burn_fil | FIL burned during miner cron events.
-- asset.column = miner_cron_fee_assessed_fil | FIL fees assessed during miner cron events.
-- asset.column = miner_cron_penalty_assessed_fil | FIL penalties assessed during miner cron events.
-- asset.column = unattributed_burn_fil | FIL burned by other mechanisms.

-- asset.not_null = date
-- asset.not_null = total_burn_fil
-- asset.not_null = message_gas_burn_fil
-- asset.not_null = message_miner_penalty_burn_fil
-- asset.not_null = miner_cron_burn_fil
-- asset.not_null = miner_cron_fee_assessed_fil
-- asset.not_null = miner_cron_penalty_assessed_fil
-- asset.not_null = unattributed_burn_fil
-- asset.unique = date

select
    network_burn.date,
    network_burn.total_burn_fil,
    coalesce(network_activity.message_burn_fil, 0) as message_gas_burn_fil,
    coalesce(network_activity.message_miner_penalty_burn_fil, 0)
        as message_miner_penalty_burn_fil,
    coalesce(miner_cron_fees.miner_cron_burn_fil, 0) as miner_cron_burn_fil,
    coalesce(miner_cron_fees.miner_cron_fee_assessed_fil, 0)
        as miner_cron_fee_assessed_fil,
    coalesce(miner_cron_fees.miner_cron_penalty_assessed_fil, 0)
        as miner_cron_penalty_assessed_fil,
    network_burn.total_burn_fil
        - coalesce(network_activity.message_burn_fil, 0)
        - coalesce(network_activity.message_miner_penalty_burn_fil, 0)
        - coalesce(miner_cron_fees.miner_cron_burn_fil, 0)
        as unattributed_burn_fil
from raw.daily_network_burn as network_burn
left join raw.daily_miner_cron_fees as miner_cron_fees
    using (date)
left join model.daily_network_activity as network_activity
    using (date)
order by date desc
