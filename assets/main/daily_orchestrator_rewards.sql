-- asset.description = Daily service rewards earned and claimed per ServiceOrchestrator and payout wallet.

-- asset.depends = model.foc_daily_orchestrator_rewards

-- asset.column = date | UTC date.
-- asset.column = orchestrator | ServiceOrchestrator identity address; NULL when unknown or ambiguous.
-- asset.column = wallet | Payout wallet.
-- asset.column = earned_atto_fil | Rewards earned, in attoFIL.
-- asset.column = claimed_atto_fil | Rewards paid out by Claim, in attoFIL.

-- Parquet has no HUGEINT (exported as lossy DOUBLE); DECIMAL(38,0) keeps atto amounts exact.
select
    date,
    orchestrator,
    wallet,
    earned_atto_fil::decimal(38, 0) as earned_atto_fil,
    claimed_atto_fil::decimal(38, 0) as claimed_atto_fil
from model.foc_daily_orchestrator_rewards
order by date desc, orchestrator, wallet
