-- asset.description = Solstice quarters with bound FPV, share submission, and gate outcome.

-- asset.depends = model.foc_service_quarters

-- asset.column = quarter | Solstice quarter number (1 = activation quarter).
-- asset.column = start_block | First epoch of the quarter.
-- asset.column = end_block | Last epoch of the quarter.
-- asset.column = posting_start_block | First epoch of the posting window (the next quarter start).
-- asset.column = verification_start_block | First epoch of the verification (correction) window.
-- asset.column = bound_block | First epoch when posted volumes are bound.
-- asset.column = as_of_block | Last epoch covered by contiguous decoded source logs (capped at UTC yesterday).
-- asset.column = is_bound | Whether source coverage reaches the bound epoch.
-- asset.column = bound_volume_atto_usd | SRA aggregated FPV (posts and corrections, removals never deducted), in atto-USD; NULL until bound.
-- asset.column = shares_submitted_at | Observed SharesSubmitted timestamp; all-zero submissions emit no event.
-- asset.column = share_recipients | Recipients in the observed submitted share map.
-- asset.column = shares_total_atto_usd | USD total over admitted recipients in the observed share map.
-- asset.column = gate_checked_at | Observed SWA gate check timestamp; quarter 1 is never gated.
-- asset.column = gate_passed | Whether the bound FPV met the gate threshold; NULL if not checked.
-- asset.column = gate_steps | Gate steps after the check.
-- asset.column = gate_threshold_atto_usd | Threshold applied (base * stepRatio^steps, FixedU18 floor math), in atto-USD; NULL if arithmetic exceeds HUGEINT.

-- Parquet has no HUGEINT (exported as lossy DOUBLE); DECIMAL(38,0) keeps atto amounts exact.
select * replace (
    bound_volume_atto_usd::decimal(38, 0) as bound_volume_atto_usd,
    shares_total_atto_usd::decimal(38, 0) as shares_total_atto_usd,
    gate_threshold_atto_usd::decimal(38, 0) as gate_threshold_atto_usd
)
from model.foc_service_quarters
