-- asset.description = Daily Dealbot probe outcomes and onchain PDP proving per service provider. Probes are not client traffic. Check types with no observations for a provider and date are NULL.

-- asset.depends = model.foc_daily_provider_checks

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
-- asset.column = proving_proofs | Accepted onchain PDP proofs of FWSS data sets. Null when onchain logs through the date are not fully decoded or the provider has no proving data set.
-- asset.column = proving_periods_closed | Proving periods closed onchain on the date, faulted or proven. Null under the same conditions as proving_proofs.
-- asset.column = proving_periods_faulted | Proving periods recorded as faulted when closed on the date; missed periods remain uncounted until closure. Null under the same conditions as proving_proofs.
-- asset.column = storage_success_rate | storage_successes over storage_checks.
-- asset.column = retrieval_success_rate | retrieval_successes over retrieval_checks.
-- asset.column = pull_success_rate | pull_successes over pull_checks.
-- asset.column = sampled_retrieval_success_rate | sampled_retrieval_successes over sampled_retrieval_checks.
-- asset.column = sampled_ipni_success_rate | sampled_ipni_successes over sampled_ipni_checks.
-- asset.column = sampled_block_fetch_success_rate | sampled_block_fetch_successes over sampled_block_fetch_checks.
-- asset.column = proving_fault_rate | proving_periods_faulted over proving_periods_closed.

-- asset.not_null = date
-- asset.assert = storage_successes <= storage_checks
-- asset.assert = retrieval_successes <= retrieval_checks
-- asset.assert = pull_successes <= pull_checks
-- asset.assert = sampled_retrieval_successes <= sampled_retrieval_checks
-- asset.assert = sampled_car_successes <= sampled_car_checks
-- asset.assert = sampled_ipni_successes <= sampled_ipni_checks
-- asset.assert = sampled_block_fetch_successes <= sampled_block_fetch_checks
-- asset.assert = proving_periods_faulted <= proving_periods_closed

select *
from model.foc_daily_provider_checks
order by date desc, provider_id
