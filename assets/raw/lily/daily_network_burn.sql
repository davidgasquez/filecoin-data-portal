-- asset.description = Daily total FIL burned, dated by the executing height.
-- asset.resource = bigquery.lily

-- asset.column = date | UTC date of the executing height.
-- asset.column = total_burn_fil | Daily total FIL burned on-chain, in FIL.

-- asset.not_null = date
-- asset.not_null = total_burn_fil
-- asset.unique = date

with by_height as (
    select
        height,
        lead(height) over (order by height) as next_height,
        date(timestamp_seconds((height * 30) + 1598306400)) as date,
        date(timestamp_seconds((lead(height) over (order by height) * 30) + 1598306400))
            as next_date,
        date(timestamp_seconds(((lead(height) over (order by height) - 1) * 30) + 1598306400))
            as last_executed_date,
        lead(cast(burnt_fil as bignumeric)) over (order by height)
            - cast(burnt_fil as bignumeric) as burn_atto
    from `chain_economics`
), incomplete_dates as (
    -- Null rounds are expected; skipped heights with blocks are missing snapshots.
    select distinct incomplete_date
    from by_height
    join `block_headers` as block_headers
        on block_headers.height > by_height.height
        and block_headers.height < by_height.next_height
    cross join unnest(
        generate_date_array(by_height.date, by_height.last_executed_date)
    ) as incomplete_date
    where by_height.last_executed_date > by_height.date
)
select
    date,
    cast(sum(burn_atto) / 1e18 as float64) as total_burn_fil
from by_height
where burn_atto is not null
    and date < current_date()
    and date not in (select incomplete_date from incomplete_dates)
group by 1
having max(next_date) > date
order by 1 desc
