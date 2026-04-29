-- asset.description = Daily Filecoin onchain activity by method from Lily BigQuery.
-- asset.resource = bigquery.lily

-- asset.not_null = date
-- asset.not_null = method

select
    date(timestamp_seconds((height * 30) + 1598306400)) as date,
    concat(
        regexp_extract(actor_name, r'[^/]+$'),
        '/',
        g.method,
        '/',
        coalesce(m.method_name, 'unknown')
    ) as method,
    sum(gas_used) / 1e6 as gas_used_millions,
    count(*) as transactions,
    cast(sum(cast(value as bignumeric) / 1e18) as float64) as total_value_fil,
    cast(sum(cast(base_fee_burn as bignumeric) / 1e18) as float64)
        as base_fee_burn_fil,
    cast(
        sum(
            (
                cast(base_fee_burn as bignumeric)
                + cast(over_estimation_burn as bignumeric)
            ) / 1e18
        ) as float64
    ) as message_burn_fil,
    cast(
        sum(
            (
                cast(base_fee_burn as bignumeric)
                + cast(over_estimation_burn as bignumeric)
                + cast(miner_tip as bignumeric)
            ) / 1e18
        ) as float64
    ) as total_gas_fee_fil
from `derived_gas_outputs` as g
left join `actor_methods` as m
    on g.method = m.method
   and regexp_extract(g.actor_name, r'[^/]+$') = m.family
group by 1, 2
order by 1 desc, 4 desc
