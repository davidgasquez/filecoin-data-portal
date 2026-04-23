-- asset.description = Daily network burn totals and message burn breakdown.

-- asset.depends = raw.daily_message_burn
-- asset.depends = raw.daily_protocol_revenue

-- asset.column = date | UTC date.
-- asset.column = total_burn_fil | Daily total FIL burned on-chain, in FIL.
-- asset.column = base_fee_burn_fil | Daily FIL burned by base fees, in FIL.
-- asset.column = over_estimation_burn_fil | Daily FIL burned by gas overestimation, in FIL.
-- asset.column = message_burn_fil | Daily FIL burned by exact message gas burn, in FIL.
-- asset.column = other_burn_fil | Residual daily FIL burned outside exact message gas burn, in FIL.

-- asset.not_null = date
-- asset.not_null = total_burn_fil
-- asset.not_null = base_fee_burn_fil
-- asset.not_null = over_estimation_burn_fil
-- asset.not_null = message_burn_fil
-- asset.not_null = other_burn_fil
-- asset.unique = date

select
    total_burn.date,
    total_burn.protocol_revenue_fil as total_burn_fil,
    coalesce(message_burn.base_fee_burn_fil, 0) as base_fee_burn_fil,
    coalesce(message_burn.over_estimation_burn_fil, 0)
        as over_estimation_burn_fil,
    coalesce(message_burn.message_burn_fil, 0) as message_burn_fil,
    total_burn.protocol_revenue_fil
        - coalesce(message_burn.message_burn_fil, 0) as other_burn_fil
from raw.daily_protocol_revenue as total_burn
left join raw.daily_message_burn as message_burn
    using (date)
order by date desc
