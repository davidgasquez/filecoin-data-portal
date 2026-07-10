-- asset.description = Daily warm storage activity.

-- asset.depends = model.fevm_daily_checkpoints
-- asset.depends = model.filecoin_pay_rail_rate_intervals
-- asset.depends = model.warm_storage_datasets

-- asset.column = date | UTC date.
-- asset.column = active_payers | Payers with at least one active chargeable dataset.
-- asset.column = active_datasets | Active chargeable datasets.
-- asset.column = new_payers | Payers whose first chargeable dataset started billing on the date.
-- asset.column = new_datasets | Datasets whose billing started on the date.

-- asset.not_null = date
-- asset.not_null = active_payers
-- asset.not_null = active_datasets
-- asset.not_null = new_payers
-- asset.not_null = new_datasets
-- asset.unique = date

with dataset_intervals as (
    select
        datasets.dataset_id,
        datasets.payer,
        intervals.start_ordinal,
        intervals.end_ordinal
    from model.warm_storage_datasets as datasets
    join model.filecoin_pay_rail_rate_intervals as intervals
        on datasets.pdp_rail_id = intervals.rail_id
    where intervals.rate_wei_per_epoch > 0
),
dataset_first_billing as (
    select
        dataset_id,
        payer,
        min(start_ordinal) as first_billing_ordinal
    from dataset_intervals
    group by 1, 2
),
dataset_first_billing_dates as (
    select
        first_billing.dataset_id,
        first_billing.payer,
        min(checkpoints.date) as first_billing_date
    from dataset_first_billing as first_billing
    join model.fevm_daily_checkpoints as checkpoints
        on first_billing.first_billing_ordinal <= checkpoints.checkpoint_ordinal
    group by 1, 2
),
days as (
    select date, checkpoint_ordinal
    from model.fevm_daily_checkpoints
    where date >= (select min(first_billing_date) from dataset_first_billing_dates)
),
payer_first_billing_dates as (
    select
        payer,
        min(first_billing_date) as first_billing_date
    from dataset_first_billing_dates
    group by 1
),
new_payers as (
    select
        first_billing_date as date,
        count(*) as new_payers
    from payer_first_billing_dates
    group by 1
),
new_datasets as (
    select
        first_billing_date as date,
        count(*) as new_datasets
    from dataset_first_billing_dates
    group by 1
),
active_counts as (
    select
        days.date,
        count(distinct intervals.payer) as active_payers,
        count(distinct intervals.dataset_id) as active_datasets
    from days
    left join dataset_intervals as intervals
        on intervals.start_ordinal <= days.checkpoint_ordinal
       and coalesce(intervals.end_ordinal, 9223372036854775807) > days.checkpoint_ordinal
    group by 1
)
select
    active_counts.date,
    active_counts.active_payers,
    active_counts.active_datasets,
    coalesce(new_payers.new_payers, 0) as new_payers,
    coalesce(new_datasets.new_datasets, 0) as new_datasets
from active_counts
left join new_payers
    using (date)
left join new_datasets
    using (date)
order by date desc
