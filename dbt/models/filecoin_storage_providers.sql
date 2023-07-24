select
    smd.provider_id,
    sum(piece_size) / 1024 ^ 5 as onboarded_tibs,
    count(distinct deal_id) as total_deals,
    count(distinct client_id) as total_clients,
    min(sector_start_at) as first_deal_at,
    max(sector_start_at) as last_deal_at,
    min(spl.country) as country
from filecoin_state_market_deals as smd
left join
    filecoin_storage_providers_locations as spl on smd.provider_id = spl.provider_id
where sector_start_epoch != -1 and slash_epoch = -1
group by 1
order by 2 desc
