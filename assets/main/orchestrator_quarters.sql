-- asset.description = Quarterly Filecoin Pay Volume (FPV) per ServiceOrchestrator: recomputed, posted, corrected, and bound.

-- asset.depends = model.foc_orchestrator_quarterly_postings
-- asset.depends = model.foc_orchestrator_quarterly_volumes
-- asset.depends = model.foc_service_quarters

-- asset.column = quarter | Solstice quarter number (1 = activation quarter).
-- asset.column = orchestrator | ServiceOrchestrator identity address.
-- asset.column = start_block | First epoch of the quarter.
-- asset.column = end_block | Last epoch of the quarter.
-- asset.column = volume_as_of_block | Last epoch counted in the recomputed volume (coverage capped at the quarter end).
-- asset.column = is_complete | Whether source coverage reaches the quarter end.
-- asset.column = stablecoin_settlements | Attributed admitted-stablecoin settlement events; NULL when source or binding coverage is unknown.
-- asset.column = stablecoin_volume_atto_usd | Attributed admitted-stablecoin gross settled amount, in atto-USD; NULL if unknown.
-- asset.column = fil_volume_atto_usd | Attributed FIL priced by the quarter's fee-auction prints, in atto-USD; NULL if unknown.
-- asset.column = fil_pending_atto_fil | Attributed FIL settled by the quarter end (or coverage) and not priced yet (rolls forward), in attoFIL; NULL if unknown.
-- asset.column = volume_atto_usd | Recomputed FPV in atto-USD (stablecoin plus FIL); NULL if any part is unknown.
-- asset.column = is_removed_in_quarter | Whether the orchestrator was removed during the quarter (excluded from the aggregate).
-- asset.column = as_of_block | Last epoch covered by contiguous decoded source logs for posts, corrections, and binding (capped at UTC yesterday).
-- asset.column = is_bound | Whether source coverage reaches the quarter's bound epoch.
-- asset.column = posted_at | VolumePosted timestamp; NULL if never posted.
-- asset.column = posted_volume_atto_usd | Initial posted volume, in atto-USD; NULL if never posted.
-- asset.column = corrections | VolumeCorrected events.
-- asset.column = corrected_at | Latest VolumeCorrected timestamp.
-- asset.column = reported_volume_atto_usd | Latest on-chain volume (post or correction; 0 clears), in atto-USD; NULL if never written.
-- asset.column = bound_volume_atto_usd | Volume counted in the SRA bound aggregate, in atto-USD; 0 if bound without writes, NULL until bound.

-- Parquet has no HUGEINT (exported as lossy DOUBLE); DECIMAL(38,0) keeps atto amounts exact.
select
    p.quarter,
    p.orchestrator,
    q.start_block,
    q.end_block,
    v.as_of_block as volume_as_of_block,
    v.is_complete,
    v.stablecoin_settlements,
    v.stablecoin_volume_atto_usd::decimal(38, 0) as stablecoin_volume_atto_usd,
    v.fil_volume_atto_usd::decimal(38, 0) as fil_volume_atto_usd,
    v.fil_pending_atto_fil::decimal(38, 0) as fil_pending_atto_fil,
    v.volume_atto_usd::decimal(38, 0) as volume_atto_usd,
    v.is_removed_in_quarter,
    p.as_of_block,
    p.is_bound,
    p.posted_at,
    p.posted_volume_atto_usd::decimal(38, 0) as posted_volume_atto_usd,
    p.corrections,
    p.corrected_at,
    p.reported_volume_atto_usd::decimal(38, 0) as reported_volume_atto_usd,
    p.bound_volume_atto_usd::decimal(38, 0) as bound_volume_atto_usd
from model.foc_orchestrator_quarterly_postings as p
join model.foc_service_quarters as q using (quarter)
left join model.foc_orchestrator_quarterly_volumes as v using (quarter, orchestrator)
order by p.quarter desc, p.orchestrator
