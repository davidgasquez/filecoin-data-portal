-- asset.description = Daily FEVM end-of-day checkpoints.

-- asset.depends = raw.fevm_eth_logs_decoded
-- asset.depends = raw.fevm_eth_logs

-- asset.column = date | UTC date.
-- asset.column = checkpoint_ordinal | Last FEVM event ordinal observed on or before the date.

-- asset.not_null = date
-- asset.not_null = checkpoint_ordinal
-- asset.unique = date

with chain_day_ordinals as (
    select
        file_date as date,
        max(block_number * 1000000 + log_index) as day_end_ordinal
    from raw.fevm_eth_logs_decoded
    where file_date <= current_date - 1
    group by 1
),
days as (
    select distinct file_date as date
    from raw.fevm_eth_logs
    where file_date between (select min(date) from chain_day_ordinals)
        and current_date - 1
)
select
    days.date,
    max(chain_day_ordinals.day_end_ordinal) over (
        order by days.date
        rows between unbounded preceding and current row
    ) as checkpoint_ordinal
from days
left join chain_day_ordinals
    using (date)
