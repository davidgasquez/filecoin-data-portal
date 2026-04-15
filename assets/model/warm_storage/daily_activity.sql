-- asset.description = Daily warm storage activity.

-- asset.depends = model.fevm_daily_checkpoints
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

with days as (
    select date
    from model.fevm_daily_checkpoints
    where date >= (
        select min(date(billing_started_at))
        from model.warm_storage_datasets
        where billing_started_at is not null
    )
),
payer_first_billing_dates as (
    select
        payer,
        min(date(billing_started_at)) as first_billing_date
    from model.warm_storage_datasets
    where billing_started_at is not null
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
        date(billing_started_at) as date,
        count(*) as new_datasets
    from model.warm_storage_datasets
    where billing_started_at is not null
    group by 1
)
select
    days.date,
    count(distinct datasets.payer) as active_payers,
    count(distinct datasets.dataset_id) as active_datasets,
    coalesce(new_payers.new_payers, 0) as new_payers,
    coalesce(new_datasets.new_datasets, 0) as new_datasets
from days
left join model.warm_storage_datasets as datasets
    on date(datasets.billing_started_at) <= days.date
   and coalesce(date(datasets.billing_terminated_at), date '9999-12-31') > days.date
left join new_payers
    using (date)
left join new_datasets
    using (date)
group by 1, 4, 5
