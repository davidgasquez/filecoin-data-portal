-- Attribution joins must neither drop nor duplicate service stream amounts.
select *
from (
    select
        (select coalesce(sum(earned_atto_fil), 0) from model.foc_daily_orchestrator_rewards) as earned,
        (select coalesce(sum(earned_atto::hugeint), 0) from raw.lily_reward_earnings where stream_id = 2) as expected_earned,
        (select coalesce(sum(claimed_atto_fil), 0) from model.foc_daily_orchestrator_rewards) as claimed,
        (select coalesce(sum(claimed_atto::hugeint), 0) from raw.lily_reward_claims where stream_id = 2) as expected_claimed
)
where earned != expected_earned
   or claimed != expected_claimed
