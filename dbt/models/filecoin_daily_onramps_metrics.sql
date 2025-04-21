with onramp_mappings as (
    select * from {{ source('raw_assets', 'raw_onramp_mappings') }}
),

daily_client_metrics as (
    select * from {{ ref('filecoin_daily_clients_metrics') }}
)

select
    dm.date,
    om.onramp_name,
    sum(dm.onboarded_data_tibs) as onboarded_data_tibs,
    sum(dm.deals) as deals,
    sum(dm.unique_piece_cids) as unique_piece_cids,
    sum(dm.unique_deal_making_providers) as unique_deal_making_providers,
    sum(dm.deal_ends) as deal_ends,
    sum(dm.ended_data_tibs) as ended_data_tibs,
from daily_client_metrics dm
full outer join onramp_mappings om on dm.client_id = om.client_id
where 1=1
    and om.onramp_name is not null
group by 1, 2
order by dm.date desc
