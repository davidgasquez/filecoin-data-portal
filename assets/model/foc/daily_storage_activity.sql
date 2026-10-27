-- asset.description = Daily warm storage billing activity from positive-rate PDP rail intervals.

-- asset.depends = model.network_daily_fevm_checkpoints
-- asset.depends = model.pay_rail_rate_intervals
-- asset.depends = model.foc_data_sets

-- asset.column = date | UTC date.
-- asset.column = billing_payers | Payers with at least one data set billing at a positive PDP rail rate at end of day.
-- asset.column = billing_data_sets | Data sets billing at a positive PDP rail rate at end of day.
-- asset.column = new_billing_payers | Payers whose first data set started billing on the date.
-- asset.column = new_billing_data_sets | Data sets whose billing started on the date.

-- asset.not_null = date
-- asset.not_null = billing_payers
-- asset.not_null = billing_data_sets
-- asset.not_null = new_billing_payers
-- asset.not_null = new_billing_data_sets
-- asset.unique = date

with billing_intervals as (
    select
        data_sets.data_set_id,
        data_sets.owner as payer,
        intervals.start_ordinal,
        intervals.end_ordinal
    from model.foc_data_sets as data_sets
    join model.pay_rail_rate_intervals as intervals
        on data_sets.pdp_rail_id = intervals.rail_id
    where intervals.rate_wei_per_epoch > 0
),
data_set_first_billing as (
    select
        data_set_id,
        payer,
        min(start_ordinal) as first_billing_ordinal
    from billing_intervals
    group by 1, 2
),
data_set_first_billing_dates as (
    select
        first_billing.data_set_id,
        first_billing.payer,
        min(checkpoints.date) as first_billing_date
    from data_set_first_billing as first_billing
    join model.network_daily_fevm_checkpoints as checkpoints
        on first_billing.first_billing_ordinal <= checkpoints.checkpoint_ordinal
    group by 1, 2
),
days as (
    select date, checkpoint_ordinal
    from model.network_daily_fevm_checkpoints
    where date >= (select min(first_billing_date) from data_set_first_billing_dates)
),
payer_first_billing_dates as (
    select
        payer,
        min(first_billing_date) as first_billing_date
    from data_set_first_billing_dates
    group by 1
),
new_billing_payers as (
    select
        first_billing_date as date,
        count(*) as new_billing_payers
    from payer_first_billing_dates
    group by 1
),
new_billing_data_sets as (
    select
        first_billing_date as date,
        count(*) as new_billing_data_sets
    from data_set_first_billing_dates
    group by 1
),
billing_counts as (
    select
        days.date,
        count(distinct intervals.payer) as billing_payers,
        count(distinct intervals.data_set_id) as billing_data_sets
    from days
    left join billing_intervals as intervals
        on intervals.start_ordinal <= days.checkpoint_ordinal
       and coalesce(intervals.end_ordinal, 9223372036854775807) > days.checkpoint_ordinal
    group by 1
)
select
    billing_counts.date,
    billing_counts.billing_payers,
    billing_counts.billing_data_sets,
    coalesce(new_billing_payers.new_billing_payers, 0) as new_billing_payers,
    coalesce(new_billing_data_sets.new_billing_data_sets, 0) as new_billing_data_sets
from billing_counts
left join new_billing_payers
    using (date)
left join new_billing_data_sets
    using (date)
order by date desc
