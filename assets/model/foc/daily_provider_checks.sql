-- asset.description = Daily Dealbot check outcomes and onchain PDP proving per service provider. Check types with no observations for a provider and date are NULL.

-- asset.depends = raw.probelab_storage_checks
-- asset.depends = raw.probelab_retrieval_checks
-- asset.depends = raw.probelab_pull_checks
-- asset.depends = raw.probelab_sampled_retrieval_checks
-- asset.depends = raw.riba_eth_logs
-- asset.depends = raw.riba_eth_logs_decoded
-- asset.depends = model.foc_data_sets

-- asset.column = date | UTC date.
-- asset.column = provider_id | Service provider registry identifier; null when a Dealbot check did not record it.
-- asset.column = storage_checks | Data storage checks that finished as created or failed.
-- asset.column = storage_successes | Data storage checks that created the deal.
-- asset.column = storage_median_upload_ms | Median upload time to the provider of created deals, in milliseconds.
-- asset.column = storage_median_confirmation_ms | Median time from piece added to piece confirmed onchain of created deals, in milliseconds.
-- asset.column = retrieval_checks | IPFS retrievals of Dealbot's own deals.
-- asset.column = retrieval_successes | Successful IPFS retrievals of Dealbot's own deals.
-- asset.column = retrieval_median_ttfb_ms | Median time to first byte of successful retrievals, in milliseconds.
-- asset.column = retrieval_p95_ttfb_ms | 95th percentile time to first byte of successful retrievals, in milliseconds.
-- asset.column = retrieval_median_bytes_per_second | Median download rate of successful retrievals, in bytes per second.
-- asset.column = pull_checks | Pull-to-park checks.
-- asset.column = pull_successes | Successful pull-to-park checks.
-- asset.column = pull_median_completion_ms | Median time from pull request to completion of successful pulls, in milliseconds.
-- asset.column = pull_p95_completion_ms | 95th percentile time from pull request to completion of successful pulls, in milliseconds.
-- asset.column = pull_median_bytes_per_second | Median piece bytes over total completion time of successful pulls, in bytes per second.
-- asset.column = sampled_retrieval_checks | Attempted piece retrievals of sampled non-Dealbot pieces.
-- asset.column = sampled_retrieval_successes | Sampled piece retrievals returning HTTP 2xx with bytes matching the piece CID.
-- asset.column = sampled_retrieval_skipped | Sampled retrieval checks skipped because no candidate piece was found.
-- asset.column = sampled_retrieval_median_ttfb_ms | Median time to first byte of successful sampled retrievals, in milliseconds.
-- asset.column = sampled_retrieval_p95_ttfb_ms | 95th percentile time to first byte of successful sampled retrievals, in milliseconds.
-- asset.column = sampled_retrieval_median_bytes_per_second | Median download rate of successful sampled retrievals, in bytes per second.
-- asset.column = sampled_car_checks | Sampled-piece checks that attempted CAR parsing. Skips are excluded; malformed CAR data is not a provider-fault measure.
-- asset.column = sampled_car_successes | Sampled-piece checks whose fetched bytes parsed as a CAR.
-- asset.column = sampled_ipni_checks | Sampled-piece checks that attempted IPNI verification. Skips are excluded.
-- asset.column = sampled_ipni_successes | Sampled IPNI lookups resolving every CID to the provider.
-- asset.column = sampled_ipni_median_verify_ms | Median IPNI verification time of successful sampled IPNI lookups, in milliseconds.
-- asset.column = sampled_block_fetch_checks | Sampled-piece checks that attempted gateway block fetches. Skips are excluded.
-- asset.column = sampled_block_fetch_successes | Sampled-piece checks where every fetched block matched its CID.
-- asset.column = proving_proofs | Accepted proofs of FWSS data sets. Null when onchain logs through the date are not fully decoded or the provider has no proving data set.
-- asset.column = proving_periods_closed | Proving periods closed by the next proving period call, faulted or proven. Null under the same conditions as proving_proofs.
-- asset.column = proving_periods_faulted | Proving periods recorded as faulted when closed; missed periods remain uncounted until closure. Null under the same conditions as proving_proofs.
-- asset.column = storage_success_rate | storage_successes over storage_checks.
-- asset.column = retrieval_success_rate | retrieval_successes over retrieval_checks.
-- asset.column = pull_success_rate | pull_successes over pull_checks.
-- asset.column = sampled_retrieval_success_rate | sampled_retrieval_successes over sampled_retrieval_checks.
-- asset.column = sampled_ipni_success_rate | sampled_ipni_successes over sampled_ipni_checks.
-- asset.column = sampled_block_fetch_success_rate | sampled_block_fetch_successes over sampled_block_fetch_checks.
-- asset.column = proving_fault_rate | proving_periods_faulted over proving_periods_closed.


with storage as (
    select
        timezone('UTC', timestamp)::date as date,
        sp_id as provider_id,
        count(*) filter (where status in ('deal_created', 'failed')) as storage_checks,
        count(*) filter (where status = 'deal_created') as storage_successes,
        median(epoch_ms(upload_ended_at) - epoch_ms(upload_started_at)) filter (where status = 'deal_created')
            as storage_median_upload_ms,
        median(epoch_ms(pieces_confirmed_at) - epoch_ms(pieces_added_at)) filter (where status = 'deal_created')
            as storage_median_confirmation_ms
    -- Backups repeat a few identical rows.
    from (select distinct * from raw.probelab_storage_checks)
    group by all
),
retrieval as (
    select
        timezone('UTC', timestamp)::date as date,
        sp_id as provider_id,
        count(*) as retrieval_checks,
        count(*) filter (where status = 'success') as retrieval_successes,
        median(first_byte_ms) filter (where status = 'success') as retrieval_median_ttfb_ms,
        quantile_cont(first_byte_ms, 0.95) filter (where status = 'success') as retrieval_p95_ttfb_ms,
        median(bytes_retrieved * 1000 / nullif(last_byte_ms, 0)) filter (where status = 'success')
            as retrieval_median_bytes_per_second
    -- Backups repeat a few identical rows.
    from (select distinct * from raw.probelab_retrieval_checks)
    group by all
),
pull as (
    select
        timezone('UTC', timestamp)::date as date,
        sp_id as provider_id,
        count(*) as pull_checks,
        count(*) filter (where status = 'success') as pull_successes,
        median(completion_latency_ms) filter (where status = 'success') as pull_median_completion_ms,
        quantile_cont(completion_latency_ms, 0.95) filter (where status = 'success') as pull_p95_completion_ms,
        median(throughput_bps) filter (where status = 'success') as pull_median_bytes_per_second
    from raw.probelab_pull_checks
    group by all
),
sampled as (
    select
        timezone('UTC', timestamp)::date as date,
        sp_id as provider_id,
        count(*) filter (where piece_fetch_status != 'skipped') as sampled_retrieval_checks,
        count(*) filter (where piece_fetch_status = 'success') as sampled_retrieval_successes,
        count(*) filter (where piece_fetch_status = 'skipped') as sampled_retrieval_skipped,
        median(first_byte_ms) filter (where piece_fetch_status = 'success')
            as sampled_retrieval_median_ttfb_ms,
        quantile_cont(first_byte_ms, 0.95) filter (where piece_fetch_status = 'success')
            as sampled_retrieval_p95_ttfb_ms,
        median(bytes_retrieved * 1000 / nullif(last_byte_ms, 0)) filter (where piece_fetch_status = 'success')
            as sampled_retrieval_median_bytes_per_second,
        -- These outcomes are independent; skipped is not a failure.
        count(*) filter (where car_status != 'skipped') as sampled_car_checks,
        count(*) filter (where car_status = 'success') as sampled_car_successes,
        count(*) filter (where ipni_status != 'skipped') as sampled_ipni_checks,
        count(*) filter (where ipni_status = 'success') as sampled_ipni_successes,
        median(ipni_verify_ms) filter (where ipni_status = 'success') as sampled_ipni_median_verify_ms,
        count(*) filter (where block_fetch_status != 'skipped') as sampled_block_fetch_checks,
        count(*) filter (where block_fetch_status = 'success') as sampled_block_fetch_successes
    -- Backups repeat a few identical rows.
    from (select distinct * from raw.probelab_sampled_retrieval_checks)
    group by all
),
-- Onchain proving of FWSS data sets; other PDP listeners record no faults.
proving_events as (
    select
        logs.event_name,
        logs.file_date as date,
        logs.block_number * 1000000 + logs.log_index as ordinal,
        data_sets.data_set_id,
        data_sets.provider_id::ubigint as provider_id,
        data_sets.settlement_end_epoch,
        cast(logs.args ->> 'leafCount' as bigint) as leaf_count,
        cast(logs.args ->> 'periodsFaulted' as bigint) as periods_faulted
    from raw.riba_eth_logs_decoded as logs
    join model.foc_data_sets as data_sets
        on data_sets.data_set_id = cast(coalesce(logs.args ->> 'setId', logs.args ->> 'dataSetId') as bigint)
    where (
        logs.contract_name = 'pdp_verifier'
        and logs.event_name in ('NextProvingPeriod', 'PossessionProven', 'DataSetDeleted')
    ) or (logs.contract_name = 'filecoin_warm_storage_service' and logs.event_name = 'FaultRecord')
),
proving_sequenced as (
    select
        *,
        -- An empty (leafCount 0) call closes periods, then the next call reactivates.
        coalesce(sum((event_name = 'NextProvingPeriod' and leaf_count = 0)::int) over (
            partition by data_set_id order by ordinal rows between unbounded preceding and 1 preceding
        ), 0) as segment,
        -- Activation calls (first, or after an empty call) close no period.
        event_name = 'NextProvingPeriod' and coalesce(lag(leaf_count) over (
            partition by data_set_id, event_name order by ordinal
        ), 0) = 0 as is_activation,
        -- The next call of the data set closes the period of each proof.
        first_value(case when event_name = 'NextProvingPeriod' then date end ignore nulls) over (
            partition by data_set_id order by ordinal rows between current row and unbounded following
        ) as closed_on
    from proving_events
),
proving_facts as (
    select date, provider_id, 1 as proofs, 0 as periods_closed, 0 as periods_faulted
    from proving_sequenced
    where event_name = 'PossessionProven'
    union all
    select closed_on, provider_id, 0, 1, 0
    from proving_sequenced
    where event_name = 'PossessionProven' and closed_on is not null
    union all
    -- FaultRecord comes from the closing call itself, so it is dated by closure too.
    select date, provider_id, 0, periods_faulted, periods_faulted
    from proving_sequenced
    where event_name = 'FaultRecord'
),
-- A data set proves from activation until an empty call, deletion, or payment termination.
proving_segments as (
    select
        provider_id,
        min(date) filter (where is_activation) as started_on,
        least(
            min(date) filter (where event_name = 'NextProvingPeriod' and leaf_count = 0),
            min(date) filter (where event_name = 'DataSetDeleted'),
            timezone('UTC', to_timestamp(any_value(settlement_end_epoch) * 30 + 1598306400))::date
        ) as ended_on
    from proving_sequenced
    group by data_set_id, provider_id, segment
),
-- Dates whose raw partition and every earlier one exist and are decoded at the same ETag,
-- so proofs closed on the date are not missing from an earlier gap.
proving_dates as (
    select file_date as date
    from (select distinct file_date, source_etag from raw.riba_eth_logs) as raw_dates
    left join (select distinct file_date, source_etag, true as is_decoded from raw.riba_eth_logs_decoded)
        using (file_date, source_etag)
    qualify bool_and(is_decoded is not null) over (order by file_date)
        and count(*) over (order by file_date) = file_date - min(file_date) over () + 1
),
proving as (
    select
        spine.date,
        spine.provider_id,
        coalesce(sum(proving_facts.proofs), 0) as proving_proofs,
        coalesce(sum(proving_facts.periods_closed), 0) as proving_periods_closed,
        coalesce(sum(proving_facts.periods_faulted), 0) as proving_periods_faulted
    from (
        select distinct
            unnest(generate_series(started_on, coalesce(ended_on, timezone('UTC', now())::date), interval 1 day))::date as date,
            provider_id
        from proving_segments
        where started_on is not null
        union
        select date, provider_id from proving_facts
    ) as spine
    semi join proving_dates
        using (date)
    left join proving_facts
        using (date, provider_id)
    group by all
),
keys as (
    select date, provider_id from storage
    union
    select date, provider_id from retrieval
    union
    select date, provider_id from pull
    union
    select date, provider_id from sampled
    union
    select date, provider_id from proving
)
select
    keys.date,
    keys.provider_id,
    storage.storage_checks,
    storage.storage_successes,
    storage.storage_median_upload_ms,
    storage.storage_median_confirmation_ms,
    retrieval.retrieval_checks,
    retrieval.retrieval_successes,
    retrieval.retrieval_median_ttfb_ms,
    retrieval.retrieval_p95_ttfb_ms,
    retrieval.retrieval_median_bytes_per_second,
    pull.pull_checks,
    pull.pull_successes,
    pull.pull_median_completion_ms,
    pull.pull_p95_completion_ms,
    pull.pull_median_bytes_per_second,
    sampled.sampled_retrieval_checks,
    sampled.sampled_retrieval_successes,
    sampled.sampled_retrieval_skipped,
    sampled.sampled_retrieval_median_ttfb_ms,
    sampled.sampled_retrieval_p95_ttfb_ms,
    sampled.sampled_retrieval_median_bytes_per_second,
    sampled.sampled_car_checks,
    sampled.sampled_car_successes,
    sampled.sampled_ipni_checks,
    sampled.sampled_ipni_successes,
    sampled.sampled_ipni_median_verify_ms,
    sampled.sampled_block_fetch_checks,
    sampled.sampled_block_fetch_successes,
    proving.proving_proofs,
    proving.proving_periods_closed,
    proving.proving_periods_faulted,
    storage.storage_successes / nullif(storage.storage_checks, 0) as storage_success_rate,
    retrieval.retrieval_successes / nullif(retrieval.retrieval_checks, 0) as retrieval_success_rate,
    pull.pull_successes / nullif(pull.pull_checks, 0) as pull_success_rate,
    sampled.sampled_retrieval_successes / nullif(sampled.sampled_retrieval_checks, 0) as sampled_retrieval_success_rate,
    sampled.sampled_ipni_successes / nullif(sampled.sampled_ipni_checks, 0) as sampled_ipni_success_rate,
    sampled.sampled_block_fetch_successes / nullif(sampled.sampled_block_fetch_checks, 0)
        as sampled_block_fetch_success_rate,
    proving.proving_periods_faulted / nullif(proving.proving_periods_closed, 0) as proving_fault_rate
from keys
left join storage
    on keys.date = storage.date and keys.provider_id is not distinct from storage.provider_id
left join retrieval
    on keys.date = retrieval.date and keys.provider_id is not distinct from retrieval.provider_id
left join pull
    on keys.date = pull.date and keys.provider_id is not distinct from pull.provider_id
left join sampled
    on keys.date = sampled.date and keys.provider_id is not distinct from sampled.provider_id
left join proving
    on keys.date = proving.date and keys.provider_id is not distinct from proving.provider_id
where keys.date <= timezone('UTC', now())::date - 1
order by keys.date desc, keys.provider_id
