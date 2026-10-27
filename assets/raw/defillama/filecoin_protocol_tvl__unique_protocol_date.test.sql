-- One snapshot per protocol and date; duplicates mean a bad daily dedup.
select date, protocol, count(*) as n
from raw.defillama_filecoin_protocol_tvl
group by 1, 2
having count(*) > 1
