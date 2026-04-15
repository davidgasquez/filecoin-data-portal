-- asset.description = Daily FEVM end-of-day checkpoints.

-- asset.depends = raw.fevm_eth_logs_decoded

-- asset.column = date | UTC date.
-- asset.column = checkpoint_ordinal | Last FEVM event ordinal observed on or before the date.

-- asset.not_null = date
-- asset.not_null = checkpoint_ordinal
-- asset.unique = date

with chain_day_ordinals as (
    select
        date(to_timestamp(block_number * 30 + 1598306400)) as date,
        max(block_number * 1000000 + log_index) as day_end_ordinal
    from raw.fevm_eth_logs_decoded
    group by 1
),
days as (
    select cast(generate_series as date) as date
    from generate_series(
        (select min(date) from chain_day_ordinals),
        (select max(date) from chain_day_ordinals),
        interval 1 day
    )
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
