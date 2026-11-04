-- One payout per Claim wallet position; duplicates mean duplicate messages or receipts.
select cid, wallet_index, count(*) as n
from raw.lily_reward_claims
group by 1, 2
having count(*) > 1
