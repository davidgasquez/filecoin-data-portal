-- asset.description = Daily mainnet Filecoin core metrics.

-- asset.depends = raw.fevm_eth_logs_decoded
-- asset.depends = raw.foc_filecoin_warm_storage_datasets
-- asset.depends = raw.foc_filecoin_pay_rail_rate_intervals
-- asset.depends = raw.daily_network_activity_by_method
-- asset.depends = raw.daily_sector_lifecycle

-- asset.column = date | UTC day for the metric snapshot.
-- asset.column = total_active_payers | Distinct payers with at least one chargeable warm storage dataset active on the day.
-- asset.column = total_active_datasets | Distinct chargeable warm storage datasets active on the day.
-- asset.column = new_active_payers | Distinct payers whose first-ever chargeable warm storage dataset began billing on the day.
-- asset.column = new_active_datasets | Distinct warm storage datasets whose billing started on the day.
-- asset.column = total_arr_usdfc | End-of-day USDFC ARR run-rate from active recurring Filecoin Pay rails.
-- asset.column = sector_onboarded_pibs | Raw sector bytes onboarded that day, in pebibytes.
-- asset.column = sector_terminated_pibs | Raw sector bytes terminated that day, in pebibytes. Before 2026-01-16 this also includes expirations.
-- asset.column = sector_expired_pibs | Raw sector bytes expired that day, in pebibytes.
-- asset.column = sector_removed_pibs | Raw sector bytes removed that day from termination or expiration, in pebibytes.
-- asset.column = gas_used_millions | Total gas used across all onchain methods that day, in millions of gas units.
-- asset.column = transactions | Total onchain transactions that day.
-- asset.column = total_value_fil | Total FIL value transferred by top-level messages that day.
-- asset.column = total_gas_fee_fil | Total FIL paid in gas fees that day, including base fee burn, overestimation burn, and miner tips.
-- asset.column = total_value_flow_fil | Total FIL value flow that day, defined as top-level message value plus gas fees.

-- asset.not_null = date
-- asset.not_null = total_active_payers
-- asset.not_null = total_active_datasets
-- asset.not_null = new_active_payers
-- asset.not_null = new_active_datasets
-- asset.not_null = total_arr_usdfc
-- asset.not_null = sector_onboarded_pibs
-- asset.not_null = sector_terminated_pibs
-- asset.not_null = sector_expired_pibs
-- asset.not_null = sector_removed_pibs
-- asset.not_null = gas_used_millions
-- asset.not_null = transactions
-- asset.not_null = total_value_fil
-- asset.not_null = total_gas_fee_fil
-- asset.not_null = total_value_flow_fil
-- asset.unique = date

with params as (
    select 1598306400 as genesis_timestamp
),
latest_chain_day as (
    select max(date(to_timestamp(block_number * 30 + (select genesis_timestamp from params)))) as latest_observed_date
    from raw.fevm_eth_logs_decoded
),
days as (
    select cast(generate_series as date) as day
    from generate_series(
        (
            select min(billing_started_date)
            from raw.foc_filecoin_warm_storage_datasets
            where billing_started_date is not null
        ),
        (select latest_observed_date from latest_chain_day),
        interval 1 day
    )
),
warm_storage_datasets_active_daily_metrics as (
    select
        days.day as date,
        count(distinct datasets.payer) as total_active_payers,
        count(distinct datasets.data_set_id) as total_active_datasets
    from days
    left join raw.foc_filecoin_warm_storage_datasets as datasets
        on datasets.billing_started_date <= days.day
       and coalesce(datasets.billing_terminated_date, date '9999-12-31') > days.day
    group by 1
),
payer_first_billing_dates as (
    select
        payer,
        min(billing_started_date) as first_billing_date
    from raw.foc_filecoin_warm_storage_datasets
    where billing_started_date is not null
    group by 1
),
warm_storage_datasets_new_payers_daily_metrics as (
    select
        first_billing_date as date,
        count(*) as new_active_payers
    from payer_first_billing_dates
    group by 1
),
warm_storage_datasets_new_datasets_daily_metrics as (
    select
        billing_started_date as date,
        count(*) as new_active_datasets
    from raw.foc_filecoin_warm_storage_datasets
    where billing_started_date is not null
    group by 1
),
chain_day_ordinals as (
    select
        date(to_timestamp(block_number * 30 + (select genesis_timestamp from params))) as date,
        max(block_number * 1000000 + log_index) as day_end_ordinal
    from raw.fevm_eth_logs_decoded
    group by 1
),
daily_chain_checkpoints as (
    select
        days.day as date,
        max(chain_day_ordinals.day_end_ordinal) over (
            order by days.day
            rows between unbounded preceding and current row
        ) as checkpoint_ordinal
    from days
    left join chain_day_ordinals
        on days.day = chain_day_ordinals.date
),
arr_daily_metrics as (
    select
        checkpoints.date,
        coalesce(sum(intervals.rate_token_per_epoch), 0) * 2880 * 365 as total_arr_usdfc
    from daily_chain_checkpoints as checkpoints
    left join raw.foc_filecoin_pay_rail_rate_intervals as intervals
        on intervals.is_arr_eligible
       and intervals.rate_wei_per_epoch > 0
       and intervals.start_ordinal <= checkpoints.checkpoint_ordinal
       and coalesce(intervals.end_ordinal, 9223372036854775807) > checkpoints.checkpoint_ordinal
    group by 1
),
sector_lifecycle_daily_metrics as (
    select
        date,
        cast(onboarded_bytes as double) / pow(1024, 5) as sector_onboarded_pibs,
        cast(terminated_bytes as double) / pow(1024, 5) as sector_terminated_pibs,
        cast(expired_bytes as double) / pow(1024, 5) as sector_expired_pibs,
        cast(removed_bytes as double) / pow(1024, 5) as sector_removed_pibs
    from raw.daily_sector_lifecycle
),
network_activity_daily_metrics as (
    select
        date,
        sum(gas_used_millions) as gas_used_millions,
        sum(transactions) as transactions,
        sum(total_value_fil) as total_value_fil,
        sum(total_gas_fee_fil) as total_gas_fee_fil,
        sum(total_value_fil) + sum(total_gas_fee_fil) as total_value_flow_fil
    from raw.daily_network_activity_by_method
    group by 1
)

select
    days.day as date,
    active_daily_metrics.total_active_payers,
    active_daily_metrics.total_active_datasets,
    coalesce(new_payers_daily_metrics.new_active_payers, 0) as new_active_payers,
    coalesce(new_datasets_daily_metrics.new_active_datasets, 0) as new_active_datasets,
    arr_daily_metrics.total_arr_usdfc,
    coalesce(sector_lifecycle_daily_metrics.sector_onboarded_pibs, 0) as sector_onboarded_pibs,
    coalesce(sector_lifecycle_daily_metrics.sector_terminated_pibs, 0) as sector_terminated_pibs,
    coalesce(sector_lifecycle_daily_metrics.sector_expired_pibs, 0) as sector_expired_pibs,
    coalesce(sector_lifecycle_daily_metrics.sector_removed_pibs, 0) as sector_removed_pibs,
    coalesce(network_activity_daily_metrics.gas_used_millions, 0) as gas_used_millions,
    coalesce(network_activity_daily_metrics.transactions, 0) as transactions,
    coalesce(network_activity_daily_metrics.total_value_fil, 0) as total_value_fil,
    coalesce(network_activity_daily_metrics.total_gas_fee_fil, 0) as total_gas_fee_fil,
    coalesce(network_activity_daily_metrics.total_value_flow_fil, 0) as total_value_flow_fil
from days
left join warm_storage_datasets_active_daily_metrics as active_daily_metrics
    on days.day = active_daily_metrics.date
left join warm_storage_datasets_new_payers_daily_metrics as new_payers_daily_metrics
    on days.day = new_payers_daily_metrics.date
left join warm_storage_datasets_new_datasets_daily_metrics as new_datasets_daily_metrics
    on days.day = new_datasets_daily_metrics.date
left join arr_daily_metrics
    on days.day = arr_daily_metrics.date
left join sector_lifecycle_daily_metrics
    on days.day = sector_lifecycle_daily_metrics.date
left join network_activity_daily_metrics
    on days.day = network_activity_daily_metrics.date
order by date desc
