-- asset.description = Daily onchain activity totals.

-- asset.depends = raw.daily_network_activity_by_method

-- asset.column = date | UTC date.
-- asset.column = gas_used_millions | Total gas used, in millions.
-- asset.column = transactions | Onchain transactions.
-- asset.column = total_value_fil | FIL transferred by top-level messages.
-- asset.column = total_gas_fee_fil | FIL paid in gas fees.
-- asset.column = total_value_flow_fil | FIL value transferred plus gas fees.

-- asset.not_null = date
-- asset.not_null = gas_used_millions
-- asset.not_null = transactions
-- asset.not_null = total_value_fil
-- asset.not_null = total_gas_fee_fil
-- asset.not_null = total_value_flow_fil
-- asset.unique = date

select
    date,
    sum(gas_used_millions) as gas_used_millions,
    sum(transactions) as transactions,
    cast(sum(total_value_fil) as double) as total_value_fil,
    cast(sum(total_gas_fee_fil) as double) as total_gas_fee_fil,
    cast(sum(total_value_fil) + sum(total_gas_fee_fil) as double)
        as total_value_flow_fil
from raw.daily_network_activity_by_method
group by 1
order by date desc
