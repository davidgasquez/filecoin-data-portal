-- asset.description = Daily total FIL burned on-chain from Lily chain economics.
-- asset.resource = bigquery.lily

-- asset.column = date | UTC date.
-- asset.column = total_burn_fil | Daily total FIL burned on-chain, in FIL.

-- asset.not_null = date
-- asset.not_null = total_burn_fil
-- asset.unique = date

with by_height as (
    select
        date(timestamp_seconds((height * 30) + 1598306400)) as date,
        cast(burnt_fil as bignumeric) as burnt_fil,
        lag(cast(burnt_fil as bignumeric)) over (order by height)
            as previous_burnt_fil
    from `chain_economics`
)
select
    date,
    cast(sum(burnt_fil - previous_burnt_fil) / 1e18 as float64)
        as total_burn_fil
from by_height
where previous_burnt_fil is not null
group by 1
order by 1 desc
